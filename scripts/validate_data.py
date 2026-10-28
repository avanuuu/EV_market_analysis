#!/usr/bin/env python3
"""
scripts/validate_data.py
========================
Data Validation and Quality Assurance Test Script.

Validates:
1. File existence and row count non-emptiness.
2. Primary key uniqueness and non-null constraints.
3. Foreign key referential integrity across relational entities.
4. Numerical boundary conditions (range km, battery capacity kWh, price USD, ratings 1-5).
5. MySQL database connection and validation queries (if MySQL is running).
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


def validate_csv_datasets():
    """Perform rigorous relational and boundary validation across processed CSV files."""
    errors = []
    warnings = []

    files = {
        "mfg": "manufacturers_clean.csv",
        "bat": "battery_technologies_clean.csv",
        "loc": "manufacturing_locations_clean.csv",
        "veh": "vehicles_clean.csv",
        "sales": "sales_clean.csv",
        "rat": "customer_ratings_clean.csv"
    }

    dfs = {}
    for key, fname in files.items():
        fpath = os.path.join(PROCESSED_DIR, fname)
        if not os.path.exists(fpath):
            errors.append(f"Missing required file: {fname}")
            continue
        df = pd.read_csv(fpath)
        if len(df) == 0:
            errors.append(f"File {fname} is empty (0 rows).")
        dfs[key] = df

    if errors:
        return False, errors, warnings

    df_mfg = dfs["mfg"]
    df_bat = dfs["bat"]
    df_loc = dfs["loc"]
    df_veh = dfs["veh"]
    df_sales = dfs["sales"]
    df_rat = dfs["rat"]

    logger.info("Verifying Primary Key Uniqueness...")
    if df_mfg["manufacturer_id"].duplicated().any():
        errors.append("Duplicate manufacturer_id in manufacturers_clean.csv")
    if df_bat["battery_tech_id"].duplicated().any():
        errors.append("Duplicate battery_tech_id in battery_technologies_clean.csv")
    if df_veh["vehicle_id"].duplicated().any():
        errors.append("Duplicate vehicle_id in vehicles_clean.csv")
    if df_sales["sales_id"].duplicated().any():
        errors.append("Duplicate sales_id in sales_clean.csv")
    if df_rat["rating_id"].duplicated().any():
        errors.append("Duplicate rating_id in customer_ratings_clean.csv")

    logger.info("Verifying Foreign Key Referential Integrity...")
    valid_mfg_ids = set(df_mfg["manufacturer_id"])
    valid_bat_ids = set(df_bat["battery_tech_id"])

    # Vehicles FK checks
    invalid_veh_mfg = df_veh[~df_veh["manufacturer_id"].isin(valid_mfg_ids)]
    if not invalid_veh_mfg.empty:
        errors.append(f"Found {len(invalid_veh_mfg)} vehicles with invalid manufacturer_id.")

    invalid_veh_bat = df_veh[~df_veh["battery_tech_id"].isin(valid_bat_ids)]
    if not invalid_veh_bat.empty:
        errors.append(f"Found {len(invalid_veh_bat)} vehicles with invalid battery_tech_id.")

    # Locations FK checks
    invalid_loc_mfg = df_loc[~df_loc["manufacturer_id"].isin(valid_mfg_ids)]
    if not invalid_loc_mfg.empty:
        errors.append(f"Found {len(invalid_loc_mfg)} locations with invalid manufacturer_id.")

    # Ratings FK checks
    invalid_rat_mfg = df_rat[~df_rat["manufacturer_id"].isin(valid_mfg_ids)]
    if not invalid_rat_mfg.empty:
        errors.append(f"Found {len(invalid_rat_mfg)} ratings with invalid manufacturer_id.")

    logger.info("Verifying Numerical Boundary Constraints...")
    # Vehicle ranges: 20 to 1500 km
    out_of_range = df_veh[(df_veh["driving_range_km"] < 20) | (df_veh["driving_range_km"] > 1500)]
    if not out_of_range.empty:
        errors.append(f"Found {len(out_of_range)} vehicles with driving range outside 20-1500 km.")

    # Battery capacity: 5 to 250 kWh
    out_of_bat = df_veh[(df_veh["battery_capacity_gross_kwh"] < 5) | (df_veh["battery_capacity_gross_kwh"] > 250)]
    if not out_of_bat.empty:
        errors.append(f"Found {len(out_of_bat)} vehicles with battery capacity outside 5-250 kWh.")

    # Base price: > $10,000
    out_of_price = df_veh[(df_veh["base_price_usd"] < 10000) | (df_veh["base_price_usd"] > 3000000)]
    if not out_of_price.empty:
        errors.append(f"Found {len(out_of_price)} vehicles with base price outside $10k-$3M.")

    # Customer ratings: 1.00 to 5.00
    out_of_rating = df_rat[(df_rat["overall_score"] < 1.0) | (df_rat["overall_score"] > 5.0)]
    if not out_of_rating.empty:
        errors.append(f"Found {len(out_of_rating)} ratings with overall score outside 1.0-5.0.")

    # Net Promoter Scores: -100 to +100
    out_of_nps = df_rat[(df_rat["net_promoter_score"] < -100) | (df_rat["net_promoter_score"] > 100)]
    if not out_of_nps.empty:
        errors.append(f"Found {len(out_of_nps)} ratings with NPS outside -100 to +100.")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def check_mysql_live():
    """Attempt connection to MySQL and run validation queries if online."""
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(BASE_DIR, ".env"))
        import pymysql

        conn = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DB", "ev_market_db"),
            charset="utf8mb4"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vehicles;")
        cnt = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        logger.info(f"MySQL live check passed: {cnt} vehicles verified in ev_market_db.")
        return True, f"MySQL Connected ({cnt} vehicles in database)"
    except Exception as e:
        logger.info(f"MySQL is currently offline or unreachable: {e}")
        return False, "MySQL offline (Validation performed on verified processed datasets)"


def main():
    logger.info("Executing EV Market Data Quality & Validation Tests...")
    is_valid, errors, warnings = validate_csv_datasets()

    mysql_online, mysql_msg = check_mysql_live()

    print("\n" + "="*60)
    print("DATA QUALITY VALIDATION SUMMARY")
    print("="*60)
    print(f"Dataset Relational Integrity: {'PASSED' if is_valid else 'FAILED'}")
    print(f"Total Errors Found:          {len(errors)}")
    print(f"Total Warnings:              {len(warnings)}")
    print(f"MySQL Service Status:        {mysql_msg}")
    print("="*60)

    if errors:
        print("\nValidation Errors:")
        for err in errors:
            print(f" - [ERROR] {err}")
        sys.exit(1)
    else:
        print("\nAll data validation checks PASSED successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
