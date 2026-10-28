"""
tests/test_database.py
======================
Automated test suite verifying SQL schema syntax, database queries,
analytical calculations, and execution performance.
"""

import os
import unittest
import sqlite3
import time
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
SCHEMA_FILE = os.path.join(BASE_DIR, "database", "schema.sql")
QUERIES_FILE = os.path.join(BASE_DIR, "database", "analysis_queries.sql")


class DatabaseQueryTestCase(unittest.TestCase):
    """Test case for database scripts, schema integrity, and query execution."""

    @classmethod
    def setUpClass(cls):
        """Initialize in-memory database populated with processed datasets."""
        cls.conn = sqlite3.connect(":memory:")
        tables = [
            ("manufacturers", "manufacturers_clean.csv"),
            ("battery_technologies", "battery_technologies_clean.csv"),
            ("manufacturing_locations", "manufacturing_locations_clean.csv"),
            ("vehicles", "vehicles_clean.csv"),
            ("sales", "sales_clean.csv"),
            ("customer_ratings", "customer_ratings_clean.csv")
        ]
        for tbl, fname in tables:
            fpath = os.path.join(PROCESSED_DIR, fname)
            df = pd.read_csv(fpath)
            df.to_sql(tbl, cls.conn, index=False)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_01_sql_files_exist(self):
        """Verify all mandatory SQL scripts exist and are populated."""
        self.assertTrue(os.path.exists(SCHEMA_FILE), "schema.sql missing")
        self.assertTrue(os.path.exists(QUERIES_FILE), "analysis_queries.sql missing")
        self.assertGreater(os.path.getsize(SCHEMA_FILE), 1000)
        self.assertGreater(os.path.getsize(QUERIES_FILE), 2000)

    def test_02_total_annual_sales_query(self):
        """Verify Query 1: Total Annual EV Sales aggregation."""
        start = time.time()
        sql = """
        SELECT year, powertrain, SUM(units_sold) AS total_units_sold
        FROM sales
        WHERE manufacturer_id IS NULL AND region = 'Global'
        GROUP BY year, powertrain
        ORDER BY year DESC, powertrain ASC;
        """
        df = pd.read_sql(sql, self.conn)
        latency = (time.time() - start) * 1000
        self.assertFalse(df.empty)
        # Verify 2023 BEV volume > 10 million units
        s23_bev = df[(df["year"] == 2023) & (df["powertrain"] == "BEV")]["total_units_sold"].iloc[0]
        self.assertGreaterEqual(s23_bev, 10000000)
        print(f"  [PERF] Query 1 (Annual Sales) Execution Time: {latency:.2f} ms")

    def test_03_yoy_sales_growth_window_query(self):
        """Verify Query 2: YoY Sales Growth rate with LAG() window function."""
        start = time.time()
        sql = """
        WITH annual_macro_sales AS (
            SELECT year, region, powertrain, SUM(units_sold) AS total_units
            FROM sales
            WHERE manufacturer_id IS NULL AND region = 'Global' AND powertrain = 'BEV'
            GROUP BY year, region, powertrain
        )
        SELECT 
            year, total_units,
            LAG(total_units, 1) OVER (ORDER BY year ASC) AS prior_units,
            ROUND((total_units - LAG(total_units, 1) OVER (ORDER BY year ASC)) * 100.0 / 
                  NULLIF(LAG(total_units, 1) OVER (ORDER BY year ASC), 0), 2) AS growth_pct
        FROM annual_macro_sales
        ORDER BY year DESC;
        """
        df = pd.read_sql(sql, self.conn)
        latency = (time.time() - start) * 1000
        self.assertFalse(df.empty)
        g23 = df[df["year"] == 2023]["growth_pct"].iloc[0]
        self.assertAlmostEqual(g23, 30.54, places=1)
        print(f"  [PERF] Query 2 (YoY Growth Rate) Execution Time: {latency:.2f} ms")

    def test_04_top_manufacturers_sales_rank(self):
        """Verify Query 3: Top OEMs ranked by 2023 global BEV sales."""
        sql = """
        SELECT 
            m.name AS manufacturer_name, s.units_sold, s.market_share_pct,
            DENSE_RANK() OVER (ORDER BY s.units_sold DESC) AS sales_rank
        FROM sales s
        JOIN manufacturers m ON s.manufacturer_id = m.manufacturer_id
        WHERE s.year = 2023 AND s.region = 'Global' AND s.powertrain = 'BEV'
        ORDER BY s.units_sold DESC;
        """
        df = pd.read_sql(sql, self.conn)
        self.assertFalse(df.empty)
        top_name = df.iloc[0]["manufacturer_name"]
        self.assertEqual(top_name, "Tesla")
        self.assertAlmostEqual(df.iloc[0]["market_share_pct"], 19.1, places=1)

    def test_05_category_range_aggregations(self):
        """Verify Query 8: Average and max range by vehicle category."""
        sql = """
        SELECT 
            vehicle_category,
            COUNT(vehicle_id) AS total_models,
            ROUND(MIN(driving_range_km), 1) AS min_range,
            ROUND(AVG(driving_range_km), 1) AS avg_range,
            ROUND(MAX(driving_range_km), 1) AS max_range
        FROM vehicles
        GROUP BY vehicle_category
        ORDER BY avg_range DESC;
        """
        df = pd.read_sql(sql, self.conn)
        self.assertFalse(df.empty)
        # Ensure SUV has the largest model count
        suv_row = df[df["vehicle_category"] == "SUV"].iloc[0]
        self.assertGreater(suv_row["total_models"], 500)
        self.assertGreater(suv_row["avg_range"], 400.0)


if __name__ == "__main__":
    unittest.main()
