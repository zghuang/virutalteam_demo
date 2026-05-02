import unittest
from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app


class TestLeadershipSummary(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_leadership_summary_returns_200(self):
        response = self.client.get("/api/dashboard/leadership-summary")
        self.assertEqual(response.status_code, 200)

    def test_leadership_summary_has_all_required_keys(self):
        response = self.client.get("/api/dashboard/leadership-summary")
        data = response.json()
        required_keys = [
            "total_articles",
            "active_sources",
            "active_alerts",
            "report_count_today",
            "top_priority_sector",
            "generated_at",
        ]
        for key in required_keys:
            self.assertIn(key, data)

    def test_total_articles_is_int(self):
        response = self.client.get("/api/dashboard/leadership-summary")
        self.assertIsInstance(response.json()["total_articles"], int)

    def test_active_sources_is_int(self):
        response = self.client.get("/api/dashboard/leadership-summary")
        self.assertIsInstance(response.json()["active_sources"], int)

    def test_active_alerts_is_int(self):
        response = self.client.get("/api/dashboard/leadership-summary")
        self.assertIsInstance(response.json()["active_alerts"], int)

    def test_report_count_today_is_int(self):
        response = self.client.get("/api/dashboard/leadership-summary")
        self.assertIsInstance(response.json()["report_count_today"], int)

    def test_top_priority_sector_is_str(self):
        response = self.client.get("/api/dashboard/leadership-summary")
        self.assertIsInstance(response.json()["top_priority_sector"], str)

    def test_generated_at_is_valid_iso_datetime(self):
        response = self.client.get("/api/dashboard/leadership-summary")
        generated_at = response.json()["generated_at"]
        parsed = datetime.fromisoformat(generated_at)
        self.assertIsInstance(parsed, datetime)


if __name__ == "__main__":
    unittest.main()
