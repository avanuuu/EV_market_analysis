#!/usr/bin/env python3
"""
scripts/run_analysis_queries.py
===============================
Executes the analytical queries defined in database/analysis_queries.sql
against the verified processed datasets.
Produces verified result tables for documentation and validation.
"""

import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

def load_data_into_sqlite():
    """Load processed CSV files into in-memory SQLite database for query execution."""
    conn = sqlite3.connect(":memory:")
    files = [
        ("manufacturers", "manufacturers_clean.csv"),
        ("battery_technologies", "battery_technologies_clean.csv"),
        ("manufacturing_locations", "manufacturing_locations_clean.csv"),
        ("vehicles", "vehicles_clean.csv"),
        ("sales", "sales_clean.csv"),
        ("customer_ratings", "customer_ratings_clean.csv")
    ]
    for tbl, fname in files:
        df = pd.read_csv(os.path.join(PROCESSED_DIR, fname))
        df.to_sql(tbl, conn, index=False)
    return conn

def run_queries():
    conn = load_data_into_sqlite()
    
    print("="*80)
    print("EXECUTING SQL ANALYSIS QUERIES ON VERIFIED EV DATASET")
    print("="*80)

    # Q1: Total Annual EV Sales
    print("\n--- QUERY 1: Total Annual Global EV Sales (Top Years) ---")
    q1 = """
    SELECT year, powertrain, SUM(units_sold) AS total_units_sold
    FROM sales
    WHERE manufacturer_id IS NULL AND region = 'Global'
    GROUP BY year, powertrain
    ORDER BY year DESC, powertrain ASC
    LIMIT 6;
    """
    print(pd.read_sql(q1, conn).to_string(index=False))

    # Q2: YoY Growth Rate
    print("\n--- QUERY 2: YoY Sales Growth Rate (Global BEVs) ---")
    q2 = """
    WITH annual_macro_sales AS (
        SELECT year, region, powertrain, SUM(units_sold) AS total_units
        FROM sales
        WHERE manufacturer_id IS NULL AND region = 'Global' AND powertrain = 'BEV'
        GROUP BY year, region, powertrain
    )
    SELECT 
        year, total_units AS current_year_sales,
        LAG(total_units, 1) OVER (ORDER BY year ASC) AS prior_year_sales,
        ROUND((total_units - LAG(total_units, 1) OVER (ORDER BY year ASC)) * 100.0 / 
              NULLIF(LAG(total_units, 1) OVER (ORDER BY year ASC), 0), 2) AS yoy_growth_percentage
    FROM annual_macro_sales
    ORDER BY year DESC
    LIMIT 6;
    """
    print(pd.read_sql(q2, conn).to_string(index=False))

    # Q3: Top Manufacturers by Sales (2023)
    print("\n--- QUERY 3: Top Manufacturers by Global BEV Sales (2023) ---")
    q3 = """
    SELECT 
        m.name AS manufacturer_name, m.country, s.units_sold, s.market_share_pct,
        DENSE_RANK() OVER (ORDER BY s.units_sold DESC) AS sales_rank
    FROM sales s
    JOIN manufacturers m ON s.manufacturer_id = m.manufacturer_id
    WHERE s.year = 2023 AND s.region = 'Global' AND s.powertrain = 'BEV'
    ORDER BY s.units_sold DESC
    LIMIT 10;
    """
    print(pd.read_sql(q3, conn).to_string(index=False))

    # Q7: Battery Tech Distribution
    print("\n--- QUERY 7: Battery Technology Distribution Across Models ---")
    q7 = """
    SELECT 
        b.chemistry_code, b.chemistry_name,
        COUNT(v.vehicle_id) AS active_models_count,
        ROUND(AVG(v.driving_range_km), 1) AS avg_range_km,
        ROUND(AVG(v.battery_capacity_gross_kwh), 1) AS avg_battery_gross_kwh,
        ROUND(AVG(v.base_price_usd), 0) AS avg_price_usd
    FROM battery_technologies b
    LEFT JOIN vehicles v ON b.battery_tech_id = v.battery_tech_id
    GROUP BY b.chemistry_code, b.chemistry_name
    ORDER BY active_models_count DESC;
    """
    print(pd.read_sql(q7, conn).to_string(index=False))

    # Q8: Range by Category
    print("\n--- QUERY 8: Driving Range Statistics by Category ---")
    q8 = """
    SELECT 
        vehicle_category,
        COUNT(vehicle_id) AS total_models,
        ROUND(MIN(driving_range_km), 1) AS min_range_km,
        ROUND(AVG(driving_range_km), 1) AS avg_range_km,
        ROUND(MAX(driving_range_km), 1) AS max_range_km,
        ROUND(AVG(energy_consumption_wh_km), 1) AS avg_wh_per_km
    FROM vehicles
    GROUP BY vehicle_category
    ORDER BY avg_range_km DESC;
    """
    print(pd.read_sql(q8, conn).to_string(index=False))

    # Q10: Manufacturing Distribution
    print("\n--- QUERY 10: Manufacturing Country Distribution ---")
    q10 = """
    SELECT 
        country, region,
        COUNT(location_id) AS plant_count,
        SUM(annual_capacity_units) AS total_capacity_units,
        ROUND(SUM(annual_capacity_units) * 100.0 / (SELECT SUM(annual_capacity_units) FROM manufacturing_locations), 2) AS share_pct
    FROM manufacturing_locations
    GROUP BY country, region
    ORDER BY total_capacity_units DESC;
    """
    print(pd.read_sql(q10, conn).to_string(index=False))

    # Q11: Customer Satisfaction
    print("\n--- QUERY 11: Customer Satisfaction Benchmarks by Manufacturer ---")
    q11 = """
    SELECT 
        m.name AS manufacturer_name, r.vehicle_category, r.overall_score,
        r.range_satisfaction, r.charging_experience, r.reliability_score, r.net_promoter_score
    FROM customer_ratings r
    JOIN manufacturers m ON r.manufacturer_id = m.manufacturer_id
    ORDER BY r.overall_score DESC
    LIMIT 8;
    """
    print(pd.read_sql(q11, conn).to_string(index=False))

    conn.close()

if __name__ == "__main__":
    run_queries()
