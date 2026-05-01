"""Semiconductor industry data ingestion service."""
import httpx
from datetime import datetime, timezone
from app.models.article import Article


class SemiconductorIngestionService:
    """Fetch semiconductor industry data from public sources."""

    SOURCES = [
        {"name": "EETimes", "url": "https://www.eetimes.com/rss/", "weight": 8},
        {"name": "AnandTech", "url": "https://www.anandtech.com/rss/", "weight": 7},
    ]

    async def fetch_news(self):
        results = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for src in self.SOURCES:
                try:
                    resp = await client.get(src["url"])
                    article = Article(
                        title=f"News from {src['name']}",
                        content=resp.text[:1000],
                        source_name=src["name"],
                        category="industry_news",
                        industry="semiconductor",
                        weight_score=src["weight"],
                    )
                    results.append(article)
                except Exception as e:
                    print(f"Failed {src['name']}: {e}")
        return results