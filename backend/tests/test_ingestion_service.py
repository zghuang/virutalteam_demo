import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone
import sys
import os
import importlib.util

services_dir = os.path.join(os.path.dirname(__file__), "..", "app", "services")
spec = importlib.util.spec_from_file_location("ingestion_service", os.path.join(services_dir, "ingestion_service.py"))
ingestion_module = importlib.util.module_from_spec(spec)

sys.modules["app"] = MagicMock()
sys.modules["app.database"] = MagicMock()
sys.modules["app.models"] = MagicMock()
sys.modules["app.models.article"] = MagicMock()
sys.modules["app.models.source"] = MagicMock()

from app.models.article import Article
from app.models.source import Source

spec.loader.exec_module(ingestion_module)
IngestionService = ingestion_module.IngestionService


class TestIngestionService(unittest.IsolatedAsyncioTestCase):

    async def test_fetch_and_store_returns_list(self):
        service = IngestionService()
        mock_response = MagicMock()
        mock_response.text = '{"results": []}'

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await service.fetch_and_store()

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), len(IngestionService.SOURCES))

    async def test_fetch_and_store_creates_articles_with_correct_fields(self):
        service = IngestionService()
        mock_response = MagicMock()
        mock_response.text = '{"results": []}'

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await service.fetch_and_store()

        for article in results:
            self.assertIsNotNone(article.title)
            self.assertIsNotNone(article.content)
            self.assertIsNotNone(article.source_name)
            self.assertEqual(article.category, "news")
            self.assertIsNotNone(article.weight_score)
            self.assertIsNotNone(article.url_hash)
            self.assertIsInstance(article.published_at, datetime)

    async def test_fetch_and_store_truncates_content_to_1000(self):
        service = IngestionService()
        long_text = "x" * 2000
        mock_response = MagicMock()
        mock_response.text = long_text

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await service.fetch_and_store()

        for article in results:
            self.assertLessEqual(len(article.content), 1000)

    async def test_fetch_and_store_handles_exception(self):
        service = IngestionService()

        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Network error")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await service.fetch_and_store()

        self.assertEqual(len(results), 0)

    async def test_sources_has_expected_entries(self):
        service = IngestionService()
        self.assertEqual(len(service.SOURCES), 2)
        self.assertEqual(service.SOURCES[0]["name"], "openFDA")
        self.assertEqual(service.SOURCES[1]["name"], "ClinicalTrials.gov")


if __name__ == "__main__":
    unittest.main()
