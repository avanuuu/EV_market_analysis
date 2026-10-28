#!/usr/bin/env python3
"""
scripts/load_database.py
========================
Automated MySQL Database Ingestion and Schema Initialization.

Loads normalized datasets from data/processed/ into MySQL database 'ev_market_db'.
Features:
- Reads database credentials from environment variables (.env)
- Executes database/schema.sql with DDL, constraints, indexes, and views
- Performs batch parameterized inserts with transaction safety
- Reconciles source CSV record counts with database table counts
- Handles connection errors gracefully with clear troubleshooting instructions
"""

import os
import sys
import logging
import pandas as pd
import pymysql
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "ev_market_db")

SCHEMA_FILE = os.path.join(BASE_DIR, "database", "schema.sql")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


def get_mysql_connection(use_db=True):
    """Establish and return PyMySQL connection."""
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB if use_db else None,
            charset="utf8mb4",
            autocommit=False,
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except pymysql.MySQLError as e:
        logger.error(f"MySQL Connection Error: {e}")
        return None


def execute_schema_sql(conn):
    """Execute SQL statements from schema.sql."""
    if not os.path.exists(SCHEMA_FILE):
        logger.error(f"Schema file not found at {SCHEMA_FILE}")
        return False

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split statements safely by semicolon while ignoring comments
    statements = []
    current_stmt = []
    for line in sql_content.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("--"):
            continue
        current_stmt.append(line)
        if trimmed.endswith(";"):
            statements.append("\n".join(current_stmt))
            current_stmt = []

    cursor = conn.cursor()
    try:
        logger.info(f"Executing {len(statements)} statements from schema.sql...")
        for stmt in statements:
            stmt_clean = stmt.strip()
            if stmt_clean:
                cursor.execute(stmt_clean)
        conn.commit()
        logger.info("Schema and views initialized successfully.")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error executing schema SQL: {e}")
        return False
    finally:
        cursor.close()


def insert_dataframe(conn, table_name, df, columns):
    """Insert DataFrame rows into MySQL table using parameterized queries."""
    cursor = conn.cursor()
    placeholders = ", ".join(["%s"] * len(columns))
    col_str = ", ".join([f"`{c}`" for c in columns])
    sql = f"INSERT INTO `{table_name}` ({col_str}) VALUES ({placeholders})"

    # Clean DataFrame: replace NaN with None for proper MySQL NULL handling
    df_clean = df[columns].copy()
    df_clean = df_clean.replace({float("nan"): None, np.nan: None})

    data_tuples = [
        tuple(None if pd.isna(val) else val for val in row)
        for row in df_clean.itertuples(index=False, name=None)
    ]

    try:
        cursor.executemany(sql, data_tuples)
        conn.commit()
        logger.info(f"Successfully loaded {len(data_tuples)} records into table `{table_name}`.")
        return len(data_tuples)
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to insert into `{table_name}`: {e}")
        raise e
    finally:
        cursor.close()


def load_all_tables(conn):
    """Load all processed CSV files into corresponding MySQL tables."""
    import numpy as np

    tasks = [
        ("manufacturers", "manufacturers_clean.csv", [
            "manufacturer_id", "name", "country", "headquarters_city", 
            "parent_group", "founded_year", "is_pure_ev_player"
        ]),
        ("battery_technologies", "battery_technologies_clean.csv", [
            "battery_tech_id", "chemistry_code", "chemistry_name", "cathode_material",
            "anode_material", "nominal_cell_voltage_v", "energy_density_wh_kg",
            "cycle_life_cycles", "thermal_stability", "cost_per_kwh_usd",
            "environmental_impact", "dominant_use_case"
        ]),
        ("manufacturing_locations", "manufacturing_locations_clean.csv", [
            "location_id", "manufacturer_id", "plant_name", "country",
            "city", "region", "facility_type", "annual_capacity_units",
            "operational_since", "latitude", "longitude"
        ]),
        ("vehicles", "vehicles_clean.csv", [
            "vehicle_id", "manufacturer_id", "model_name", "variant_name",
            "model_year", "vehicle_category", "drivetrain", "battery_tech_id",
            "battery_capacity_gross_kwh", "battery_capacity_net_kwh", "driving_range_km",
            "energy_consumption_wh_km", "acceleration_0_100_s", "top_speed_kmh",
            "dc_max_charge_power_kw", "ac_max_charge_power_kw", "charge_time_10_80_min",
            "base_price_usd", "origin_country", "sources"
        ]),
        ("sales", "sales_clean.csv", [
            "sales_id", "year", "region", "manufacturer_id", "vehicle_category",
            "powertrain", "units_sold", "market_share_pct", "yoy_growth_pct"
        ]),
        ("customer_ratings", "customer_ratings_clean.csv", [
            "rating_id", "manufacturer_id", "vehicle_category", "survey_year",
            "sample_size", "overall_score", "range_satisfaction", "charging_experience",
            "reliability_score", "build_quality_score", "software_infotainment_score",
            "value_for_money", "net_promoter_score", "source_note"
        ])
    ]

    summary = {}
    for table_name, csv_file, cols in tasks:
        file_path = os.path.join(PROCESSED_DIR, csv_file)
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}. Skipping table `{table_name}`.")
            continue
        df = pd.read_csv(file_path)
        count = insert_dataframe(conn, table_name, df, cols)
        summary[table_name] = count

    return summary


def verify_database_records(conn, expected_summary):
    """Verify table counts in MySQL match expected CSV counts."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 'manufacturers' AS tbl, COUNT(*) AS cnt FROM manufacturers UNION ALL
        SELECT 'battery_technologies', COUNT(*) FROM battery_technologies UNION ALL
        SELECT 'manufacturing_locations', COUNT(*) FROM manufacturing_locations UNION ALL
        SELECT 'vehicles', COUNT(*) FROM vehicles UNION ALL
        SELECT 'sales', COUNT(*) FROM sales UNION ALL
        SELECT 'customer_ratings', COUNT(*) FROM customer_ratings;
    """)
    rows = cursor.fetchall()
    cursor.close()

    logger.info("=== MySQL Record Count Reconciliation ===")
    all_match = True
    for r in rows:
        tbl = r["tbl"]
        actual = r["cnt"]
        expected = expected_summary.get(tbl, 0)
        match_str = "MATCH" if actual == expected else "MISMATCH"
        logger.info(f"Table `{tbl}`: Actual={actual} | Expected={expected} | Status={match_str}")
        if actual != expected:
            all_match = False
    return all_match


def main():
    logger.info("Initiating MySQL Database Ingestion Pipeline...")
    logger.info(f"Target Database: {MYSQL_USER}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")

    # Check initial connection to MySQL server
    conn = get_mysql_connection(use_db=False)
    if not conn:
        logger.error("Could not connect to MySQL server.")
        logger.info("\n" + "="*70)
        logger.info("HOW TO START MYSQL ON MACOS:")
        logger.info("1. Install MySQL via Homebrew: brew install mysql")
        logger.info("2. Start MySQL background service: brew services start mysql")
        logger.info("3. Verify running service: mysql -u root")
        logger.info("4. Re-run this ingestion script: python3 scripts/load_database.py")
        logger.info("="*70 + "\n")
        sys.exit(1)

    try:
        # Create database if missing
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
        cursor.close()
        conn.close()

        # Connect to specific database
        conn = get_mysql_connection(use_db=True)
        if not conn:
            sys.exit(1)

        # Execute schema
        schema_ok = execute_schema_sql(conn)
        if not schema_ok:
            logger.error("Schema initialization failed.")
            sys.exit(1)

        # Ingest tables
        summary = load_all_tables(conn)

        # Validate
        verified = verify_database_records(conn, summary)
        if verified:
            logger.info("Database ingestion and reconciliation completed successfully!")
        else:
            logger.warning("Database ingestion completed with record discrepancies.")

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
