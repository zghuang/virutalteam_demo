import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.analysis_service import AnalysisService


class TestAnalysisService:

    @pytest.fixture
    def service(self):
        return AnalysisService(api_key="sk-test", model="test-model")

    @pytest.mark.asyncio
    async def test_summarize_short_text(self, service):
        result = await service.summarize("Short")
        assert result == "Text too short to summarize."

    @pytest.mark.asyncio
    async def test_summarize_normal_text(self, service):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Mocked summary result"}}]
        }
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            result = await service.summarize("This is a long enough text to trigger the LLM summarization call successfully.")
        assert result == "Mocked summary result"

    @pytest.mark.asyncio
    async def test_analyze_sentiment_valid_json(self, service):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": json.dumps({"sentiment": "positive", "score": 0.85})}}]
        }
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            result = await service.analyze_sentiment("Great results this quarter!")
        assert result == {"sentiment": "positive", "score": 0.85}

    @pytest.mark.asyncio
    async def test_analyze_sentiment_invalid_json(self, service):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "This is not valid JSON"}}]
        }
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            result = await service.analyze_sentiment("Some text")
        assert result == {"sentiment": "neutral", "score": 0.5}

    @pytest.mark.asyncio
    async def test_detect_trends_valid_json(self, service):
        expected_trends = [
            {"trend": "AI chips", "count": 5, "keywords": ["AI", "chips"]},
            {"trend": "Biotech", "count": 3, "keywords": ["biotech", "FDA"]}
        ]
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(expected_trends)}}]
        }
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            result = await service.detect_trends(["AI chip demand surges", "Biotech breakthrough"])
        assert result == expected_trends

    @pytest.mark.asyncio
    async def test_detect_trends_invalid_json(self, service):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Not JSON"}}]
        }
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            result = await service.detect_trends(["Some title"])
        assert result == []

    @pytest.mark.asyncio
    async def test_extract_insights_valid_json(self, service):
        expected_insights = [
            {"insight": "Market growth", "importance": 4, "related_companies": ["AAPL"]}
        ]
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(expected_insights)}}]
        }
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            result = await service.extract_insights(["Long article text about market growth"])
        assert result == expected_insights

    @pytest.mark.asyncio
    async def test_extract_insights_invalid_json(self, service):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Not valid JSON at all"}}]
        }
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            result = await service.extract_insights(["Some article"])
        assert result == [{"insight": "Analysis unavailable", "importance": 1, "related_companies": []}]

    @pytest.mark.asyncio
    async def test_generate_report_valid_json(self, service):
        expected_report = {
            "executive_summary": "Key findings on semiconductors.",
            "key_findings": ["Finding 1", "Finding 2"],
            "recommendations": ["Invest in AI chips"],
            "confidence": 0.9
        }
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(expected_report)}}]
        }
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            result = await service.generate_report("semiconductors", ["Article about semiconductor market"])
        assert result == expected_report

    @pytest.mark.asyncio
    async def test_generate_report_invalid_json(self, service):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Broken response"}}]
        }
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            result = await service.generate_report("topic", ["Some text"])
        assert result == {
            "executive_summary": "Report generation pending.",
            "key_findings": [],
            "recommendations": [],
            "confidence": 0.0
        }
