import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone
import sys
import os
import importlib.util

services_dir = os.path.join(os.path.dirname(__file__), "..", "app", "services")
spec = importlib.util.spec_from_file_location("financial_ingestion", os.path.join(services_dir, "financial_ingestion.py"))
financial_module = importlib.util.module_from_spec(spec)

sys.modules["app"] = MagicMock()
sys.modules["app.database"] = MagicMock()
sys.modules["app.models"] = MagicMock()
sys.modules["app.models.financial_data"] = MagicMock()

from app.models.financial_data import FinancialData

spec.loader.exec_module(financial_module)
FinancialIngestionService = financial_module.FinancialIngestionService
FinancialIngestionError = financial_module.FinancialIngestionError


class TestTickerToCik(unittest.TestCase):

    def test_known_ticker_returns_cik(self):
        cik = FinancialIngestionService.ticker_to_cik("AAPL")
        self.assertEqual(cik, "0000320193")

    def test_ticker_is_case_insensitive(self):
        cik = FinancialIngestionService.ticker_to_cik("aapl")
        self.assertEqual(cik, "0000320193")

    def test_ticker_with_whitespace(self):
        cik = FinancialIngestionService.ticker_to_cik("  MSFT  ")
        self.assertEqual(cik, "0000789019")

    def test_unknown_ticker_raises_error(self):
        with self.assertRaises(FinancialIngestionError):
            FinancialIngestionService.ticker_to_cik("XYZXYZ")


class TestBuildFilingUrl(unittest.TestCase):

    def test_returns_correct_url(self):
        url = FinancialIngestionService._build_filing_url("0000320193-23-000106")
        self.assertIn("sec.gov", url)
        self.assertIn("000032019323000106", url)

    def test_returns_none_for_empty(self):
        url = FinancialIngestionService._build_filing_url(None)
        self.assertIsNone(url)

    def test_returns_none_for_empty_string(self):
        url = FinancialIngestionService._build_filing_url("")
        self.assertIsNone(url)


class TestParseFilingDate(unittest.TestCase):

    def test_parses_valid_date(self):
        dt = FinancialIngestionService._parse_filing_date("2024-01-15")
        self.assertEqual(dt.year, 2024)
        self.assertEqual(dt.month, 1)
        self.assertEqual(dt.day, 15)
        self.assertIsNotNone(dt.tzinfo)

    def test_returns_none_for_invalid_format(self):
        dt = FinancialIngestionService._parse_filing_date("01/15/2024")
        self.assertIsNone(dt)

    def test_returns_none_for_none(self):
        dt = FinancialIngestionService._parse_filing_date(None)
        self.assertIsNone(dt)

    def test_returns_none_for_empty_string(self):
        dt = FinancialIngestionService._parse_filing_date("")
        self.assertIsNone(dt)


class TestFetchCompanyFilings(unittest.IsolatedAsyncioTestCase):

    async def test_returns_filings_list(self):
        service = FinancialIngestionService(db=MagicMock())

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "filings": {
                "recent": {
                    "form": ["10-K", "10-Q", "8-K"],
                    "filingDate": ["2024-01-15", "2024-04-15", "2024-03-01"],
                    "accessionNumber": ["001-001", "001-002", "001-003"],
                }
            }
        }

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await service.fetch_company_filings("AAPL")

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.assertTrue(all(f["form_type"] in ("10-K", "10-Q") for f in results))

    async def test_filters_only_10k_and_10q(self):
        service = FinancialIngestionService(db=MagicMock())

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "filings": {
                "recent": {
                    "form": ["8-K", "DEF 14A", "SC 13G"],
                    "filingDate": ["2024-01-15", "2024-02-15", "2024-03-15"],
                    "accessionNumber": ["001-001", "001-002", "001-003"],
                }
            }
        }

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await service.fetch_company_filings("MSFT")

        self.assertEqual(len(results), 0)

    async def test_raises_on_non_200(self):
        service = FinancialIngestionService(db=MagicMock())

        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            with self.assertRaises(FinancialIngestionError):
                await service.fetch_company_filings("AAPL")

    async def test_raises_on_unknown_ticker(self):
        service = FinancialIngestionService(db=MagicMock())

        with self.assertRaises(FinancialIngestionError):
            await service.fetch_company_filings("NONEXISTENT")


class TestStoreFinancialData(unittest.TestCase):

    def test_stores_records_and_returns_them(self):
        mock_db = MagicMock()
        service = FinancialIngestionService(db=mock_db)

        filings = [
            {"form_type": "10-K", "filing_date": "2024-01-15", "accession_number": "001-001"},
            {"form_type": "10-Q", "filing_date": "2024-04-15", "accession_number": "001-002"},
        ]

        records = service.store_financial_data("AAPL", filings)

        self.assertEqual(len(records), 2)
        self.assertEqual(mock_db.add.call_count, 2)
        mock_db.commit.assert_called_once()

    def test_records_have_correct_fields(self):
        mock_db = MagicMock()
        service = FinancialIngestionService(db=mock_db)

        filings = [
            {"form_type": "10-K", "filing_date": "2024-01-15", "accession_number": "001-001"},
        ]

        service.store_financial_data("AAPL", filings)

        call_kwargs = mock_db.add.call_args[0][0]
        self.assertEqual(call_kwargs.company_name, "AAPL")
        self.assertEqual(call_kwargs.ticker, "AAPL")
        self.assertEqual(call_kwargs.data_type, "10-K")
        self.assertEqual(call_kwargs.currency, "USD")
        self.assertIsNotNone(call_kwargs.source_url)
        self.assertIsNotNone(call_kwargs.published_at)


class TestIngest(unittest.IsolatedAsyncioTestCase):

    async def test_ingest_fetches_and_stores(self):
        mock_db = MagicMock()
        service = FinancialIngestionService(db=mock_db)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "filings": {
                "recent": {
                    "form": ["10-K"],
                    "filingDate": ["2024-01-15"],
                    "accessionNumber": ["001-001"],
                }
            }
        }

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await service.ingest("AAPL")

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        mock_db.commit.assert_called_once()


class TestCikMap(unittest.TestCase):

    def test_cik_map_has_expected_entries(self):
        service = FinancialIngestionService(db=MagicMock())
        self.assertIn("AAPL", financial_module.CIK_MAP)
        self.assertIn("MSFT", financial_module.CIK_MAP)
        self.assertIn("GOOGL", financial_module.CIK_MAP)
        self.assertEqual(len(financial_module.CIK_MAP), 20)


if __name__ == "__main__":
    unittest.main()
