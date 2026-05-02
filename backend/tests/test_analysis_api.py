import unittest
from fastapi.testclient import TestClient

from app.main import app


class TestAnalysisAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_summarize_endpoint(self):
        response = self.client.post("/api/analysis/summarize", json=[1, 2, 3])
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Summarization endpoint ready")
        self.assertEqual(data["text_ids"], [1, 2, 3])

    def test_sentiment_endpoint(self):
        response = self.client.post("/api/analysis/sentiment", json=[42])
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Sentiment endpoint ready")

    def test_trends_endpoint(self):
        response = self.client.post("/api/analysis/trends?timeframe=30d")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Trend detection endpoint ready")
        self.assertEqual(data["timeframe"], "30d")

    def test_insights_endpoint(self):
        response = self.client.post("/api/analysis/insights?topic=semiconductors")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Insights endpoint ready")
        self.assertEqual(data["topic"], "semiconductors")


if __name__ == "__main__":
    unittest.main()
