"""
tests/test_routes.py
====================
Automated test suite verifying Flask web application routes, HTTP status codes,
security headers, pagination, search filters, and API endpoints.
"""

import unittest
import json
import time
from app import create_app


class FlaskRoutesTestCase(unittest.TestCase):
    """Test case for web routes and HTTP responses."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

    def test_01_index_route(self):
        """Verify home page loads with HTTP 200 and executive branding."""
        start_time = time.time()
        response = self.client.get("/")
        elapsed = (time.time() - start_time) * 1000
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Electric Vehicle (EV) Market Analysis", response.data)
        self.assertIn(b"Global BEV Sales", response.data)
        print(f"  [PERF] GET / response time: {elapsed:.2f} ms")

    def test_02_overview_route(self):
        """Verify market overview page loads with tables and metrics."""
        response = self.client.get("/overview")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Global EV Market Overview", response.data)
        self.assertIn(b"Top 10 Global Electric Vehicle Manufacturers", response.data)

    def test_03_dashboard_route(self):
        """Verify Tableau dashboard embed page renders properly."""
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Interactive Tableau Business Intelligence Dashboards", response.data)
        self.assertIn(b"tableauDashboardFrame", response.data)

    def test_04_story_route(self):
        """Verify Tableau Story page renders 5 narrative points."""
        response = self.client.get("/story")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Tableau Analytical Story Walkthrough", response.data)
        self.assertIn(b"Scene 1", response.data)
        self.assertIn(b"Scene 5", response.data)

    def test_05_vehicles_catalog_and_filter(self):
        """Verify vehicles catalog with search and filter parameters."""
        # Baseline catalog
        resp_base = self.client.get("/vehicles")
        self.assertEqual(resp_base.status_code, 200)
        self.assertIn(b"Electric Vehicle Database Explorer", resp_base.data)

        # Filtered query
        resp_filter = self.client.get("/vehicles?search=Tesla&category=SUV")
        self.assertEqual(resp_filter.status_code, 200)
        self.assertIn(b"Tesla", resp_filter.data)

        # Pagination test
        resp_page2 = self.client.get("/vehicles?page=2")
        self.assertEqual(resp_page2.status_code, 200)

    def test_06_methodology_and_findings(self):
        """Verify methodology and strategic findings pages."""
        resp_meth = self.client.get("/methodology")
        self.assertEqual(resp_meth.status_code, 200)
        self.assertIn(b"Data Acquisition & Legal Provenance", resp_meth.data)

        resp_find = self.client.get("/findings")
        self.assertEqual(resp_find.status_code, 200)
        self.assertIn(b"Market Strategy Director", resp_find.data)
        self.assertIn(b"Automotive Business Intelligence Manager", resp_find.data)

    def test_07_health_endpoint(self):
        """Verify /health endpoint returns JSON status 200."""
        start_time = time.time()
        response = self.client.get("/health")
        elapsed = (time.time() - start_time) * 1000
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        data = json.loads(response.data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("database", data)
        print(f"  [PERF] GET /health response time: {elapsed:.2f} ms")

    def test_08_rest_api_kpis_and_trends(self):
        """Verify REST API KPI and trend data endpoints."""
        resp_kpi = self.client.get("/api/kpis")
        self.assertEqual(resp_kpi.status_code, 200)
        kpi_data = json.loads(resp_kpi.data)
        self.assertGreater(kpi_data["total_vehicle_models"], 1000)
        self.assertGreater(kpi_data["avg_driving_range_km"], 400)

        resp_trends = self.client.get("/api/trends")
        self.assertEqual(resp_trends.status_code, 200)
        trends_data = json.loads(resp_trends.data)
        self.assertIsInstance(trends_data, list)
        self.assertGreater(len(trends_data), 5)

    def test_09_security_headers(self):
        """Verify essential security headers are present in HTTP responses."""
        response = self.client.get("/")
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("X-Frame-Options"), "SAMEORIGIN")
        self.assertEqual(response.headers.get("X-XSS-Protection"), "1; mode=block")
        self.assertIn("Content-Security-Policy", response.headers)

    def test_10_404_error_handler(self):
        """Verify custom 404 page is returned for unknown URLs."""
        response = self.client.get("/non_existent_page_path")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Page Not Found", response.data)


if __name__ == "__main__":
    unittest.main()
