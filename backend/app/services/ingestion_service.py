import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.article import Article
from app.models.source import Source
import hashlib


class IngestionService:
    SOURCES = [
        {"name": "openFDA", "url": "https://api.fda.gov/drug/event.json", "limit": 10, "weight": 10},
        {"name": "ClinicalTrials.gov", "url": "https://clinicaltrials.gov/api/query/study_values?fmt=json", "limit": 10, "weight": 10},
    ]

    async def fetch_and_store(self):
        results = []
        for src in self.SOURCES:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(src["url"], timeout=30)
                    url_hash = hashlib.md5(f"{src['name']}_{datetime.now().isoformat()}".encode()).hexdigest()
                    article = Article(
                        title=f"Data from {src['name']}",
                        content=resp.text[:1000],
                        source_name=src["name"],
                        category="news",
                        weight_score=src["weight"],
                        url_hash=url_hash,
                        published_at=datetime.now(timezone.utc)
                    )
                    results.append(article)
            except Exception as e:
                print(f"Failed to fetch {src['name']}: {e}")
        return results
