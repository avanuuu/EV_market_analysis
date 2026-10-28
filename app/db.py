"""
app/db.py
=========
Database connector and abstraction layer for the EV Market Analysis application.
Handles MySQL connections via SQLAlchemy / PyMySQL with graceful fallback
to verified processed datasets when MySQL service is offline.
"""

import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pymysql

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

_engine = None
_mysql_available = None


def _get_cfg_val(cfg, key, default=None):
    """Safely extract config values from class, object, or dict."""
    if cfg is None:
        return default
    if hasattr(cfg, key):
        val = getattr(cfg, key)
        if val is not None:
            return val
    if hasattr(cfg, "get"):
        return cfg.get(key, default)
    return default


def get_engine(config=None):
    """Obtain or initialize SQLAlchemy engine for MySQL."""
    global _engine, _mysql_available
    if _engine is not None:
        return _engine

    from config import Config
    cfg = config or Config
    host = _get_cfg_val(cfg, "MYSQL_HOST", "localhost")
    port = int(_get_cfg_val(cfg, "MYSQL_PORT", 3306))
    user = _get_cfg_val(cfg, "MYSQL_USER", "root")
    pwd = _get_cfg_val(cfg, "MYSQL_PASSWORD", "")
    db = _get_cfg_val(cfg, "MYSQL_DB", "ev_market_db")

    uri = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}?charset=utf8mb4"

    try:
        # Test connection with short timeout to prevent blocking
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=pwd,
            database=db,
            connect_timeout=1
        )
        conn.close()
        _engine = create_engine(uri, pool_pre_ping=True, pool_recycle=300)
        _mysql_available = True
        logger.info(f"Connected to MySQL Database: {db} on {host}:{port}")
    except Exception as e:
        _mysql_available = False
        _engine = None
        logger.warning(f"MySQL connection unavailable ({e}). Using processed CSV data fallback.")

    return _engine


def check_mysql_status(config=None):
    """Check MySQL database availability and record counts."""
    from config import Config
    cfg = config or Config
    host = _get_cfg_val(cfg, "MYSQL_HOST", "localhost")
    port = int(_get_cfg_val(cfg, "MYSQL_PORT", 3306))
    user = _get_cfg_val(cfg, "MYSQL_USER", "root")
    pwd = _get_cfg_val(cfg, "MYSQL_PASSWORD", "")
    db = _get_cfg_val(cfg, "MYSQL_DB", "ev_market_db")

    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=pwd,
            database=db,
            connect_timeout=1
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vehicles;")
        veh_cnt = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return {
            "status": "ONLINE",
            "connected": True,
            "host": host,
            "port": port,
            "database": db,
            "vehicles_count": veh_cnt,
            "message": "Connected to active MySQL database instance."
        }
    except Exception as e:
        return {
            "status": "OFFLINE",
            "connected": False,
            "host": host,
            "port": port,
            "database": db,
            "vehicles_count": 1149, # From verified CSV
            "message": f"MySQL server not responding ({e}). Running in resilient fallback mode."
        }


def load_table_dataframe(table_name: str) -> pd.DataFrame:
    """
    Load a table from MySQL if connected, or fallback to the verified CSV file.
    Always returns a clean pandas DataFrame.
    """
    engine = get_engine()
    if engine and _mysql_available:
        try:
            with engine.connect() as conn:
                df = pd.read_sql_table(table_name, conn)
                return df
        except SQLAlchemyError as e:
            logger.warning(f"MySQL query failed for table {table_name}: {e}. Falling back to CSV.")

    # Resilient fallback to processed CSV datasets
    csv_map = {
        "manufacturers": "manufacturers_clean.csv",
        "battery_technologies": "battery_technologies_clean.csv",
        "manufacturing_locations": "manufacturing_locations_clean.csv",
        "vehicles": "vehicles_clean.csv",
        "sales": "sales_clean.csv",
        "customer_ratings": "customer_ratings_clean.csv",
        "master_tableau": "ev_market_master_tableau.csv"
    }
    fname = csv_map.get(table_name, f"{table_name}_clean.csv")
    fpath = os.path.join(PROCESSED_DIR, fname)
    if os.path.exists(fpath):
        return pd.read_csv(fpath)
    logger.error(f"Data file for table `{table_name}` not found at {fpath}")
    return pd.DataFrame()
