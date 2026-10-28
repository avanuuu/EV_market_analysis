"""
tests/test_data_quality.py
==========================
Automated test suite verifying data cleaning results, entity referential integrity,
schema constraints, and boundary validation rules.
"""

import os
import unittest
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DQ_REPORT_PATH = os.path.join(PROCESSED_DIR, "data_quality_report.json")


class DataQualityTestCase(unittest.TestCase):
    """Test case for dataset quality, integrity, and constraints."""

    @classmethod
    def setUpClass(cls):
        cls.df_mfg = pd.read_csv(os.path.join(PROCESSED_DIR, "manufacturers_clean.csv"))
        cls.df_bat = pd.read_csv(os.path.join(PROCESSED_DIR, "battery_technologies_clean.csv"))
        cls.df_loc = pd.read_csv(os.path.join(PROCESSED_DIR, "manufacturing_locations_clean.csv"))
        cls.df_veh = pd.read_csv(os.path.join(PROCESSED_DIR, "vehicles_clean.csv"))
        cls.df_sales = pd.read_csv(os.path.join(PROCESSED_DIR, "sales_clean.csv"))
        cls.df_rat = pd.read_csv(os.path.join(PROCESSED_DIR, "customer_ratings_clean.csv"))

    def test_01_record_counts_positive(self):
        """Verify cleaned tables have expected non-zero record counts."""
        self.assertGreaterEqual(len(self.df_mfg), 70)
        self.assertGreaterEqual(len(self.df_bat), 5)
        self.assertGreaterEqual(len(self.df_loc), 15)
        self.assertGreaterEqual(len(self.df_veh), 1100)
        self.assertGreaterEqual(len(self.df_sales), 800)
        self.assertGreaterEqual(len(self.df_rat), 20)

    def test_02_primary_key_uniqueness(self):
        """Verify primary keys have zero duplicates."""
        self.assertFalse(self.df_mfg["manufacturer_id"].duplicated().any())
        self.assertFalse(self.df_bat["battery_tech_id"].duplicated().any())
        self.assertFalse(self.df_veh["vehicle_id"].duplicated().any())
        self.assertFalse(self.df_sales["sales_id"].duplicated().any())
        self.assertFalse(self.df_rat["rating_id"].duplicated().any())

    def test_03_foreign_key_integrity(self):
        """Verify all foreign keys reference valid parent records."""
        valid_mfg_ids = set(self.df_mfg["manufacturer_id"])
        valid_bat_ids = set(self.df_bat["battery_tech_id"])

        # Vehicles FKs
        self.assertTrue(self.df_veh["manufacturer_id"].isin(valid_mfg_ids).all())
        self.assertTrue(self.df_veh["battery_tech_id"].isin(valid_bat_ids).all())

        # Locations FK
        self.assertTrue(self.df_loc["manufacturer_id"].isin(valid_mfg_ids).all())

        # Ratings FK
        self.assertTrue(self.df_rat["manufacturer_id"].isin(valid_mfg_ids).all())

    def test_04_vehicle_numerical_boundaries(self):
        """Verify vehicle metrics fall within plausible real-world ranges."""
        # Range: 20 to 1200 km
        self.assertTrue((self.df_veh["driving_range_km"] >= 20).all())
        self.assertTrue((self.df_veh["driving_range_km"] <= 1200).all())

        # Battery: 5 to 250 kWh
        self.assertTrue((self.df_veh["battery_capacity_gross_kwh"] >= 5).all())
        self.assertTrue((self.df_veh["battery_capacity_gross_kwh"] <= 250).all())

        # Base price: > $10,000
        self.assertTrue((self.df_veh["base_price_usd"] >= 10000).all())

    def test_05_customer_rating_boundaries(self):
        """Verify rating scores conform to 1.00 - 5.00 bounds."""
        self.assertTrue((self.df_rat["overall_score"] >= 1.0).all())
        self.assertTrue((self.df_rat["overall_score"] <= 5.0).all())
        self.assertTrue((self.df_rat["net_promoter_score"] >= -100).all())
        self.assertTrue((self.df_rat["net_promoter_score"] <= 100).all())

    def test_06_data_quality_report_json(self):
        """Verify data quality report JSON exists and reflects successful execution."""
        self.assertTrue(os.path.exists(DQ_REPORT_PATH))
        with open(DQ_REPORT_PATH, "r") as f:
            data = json.load(f)
        self.assertEqual(data["data_pipeline_status"], "SUCCESS")
        self.assertEqual(data["validation_metrics"]["null_values_in_primary_keys"], 0)


if __name__ == "__main__":
    unittest.main()
