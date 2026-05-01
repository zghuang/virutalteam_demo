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
        # Pharma (weight 10)
        {"name": "openFDA", "url": "https://api.fda.gov/drug/event.json", "limit": 10, "weight": 10, "industry": "pharma", "category": "regulatory"},
        {"name": "ClinicalTrials.gov", "url": "https://clinicaltrials.gov/api/query/study_values?fmt=json", "limit": 10, "weight": 10, "industry": "pharma", "category": "clinical_trials"},
        # Life Science (weight 8-9)
        {"name": "PubMed", "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=10", "limit": 10, "weight": 9, "industry": "lifescience", "category": "research"},
        {"name": "BioRxiv", "url": "https://api.biorxiv.org/details/biorxiv/2020-01/01/2024-01-01/10", "limit": 5, "weight": 8, "industry": "lifescience", "category": "preprints"},
        # Semiconductor (weight 7-9)
        {"name": "EETimes", "url": "https://www.eetimes.com/rss/", "limit": 10, "weight": 8, "industry": "semiconductor", "category": "industry_news"},
        {"name": "AnandTech", "url": "https://www.anandtech.com/rss/", "limit": 10, "weight": 7, "industry": "semiconductor", "category": "industry_news"},
        {"name": "SEMI", "url": "https://www.semi.org/rss", "limit": 5, "weight": 8, "industry": "semiconductor", "category": "industry_news"},
        {"name": "EETAsia", "url": "https://www.eetasia.com/rss/", "limit": 5, "weight": 7, "industry": "semiconductor", "category": "industry_news"},
        # Financial (cross-industry)
        {"name": "SEC EDGAR", "url": "https://data.sec.gov/submissions/", "limit": 5, "weight": 10, "industry": "cross", "category": "financial"},
    ]
    
    async def fetch_and_store(self, industry_filter=None):
        results = []
        for src in self.SOURCES:
            if industry_filter and src["industry"] != industry_filter and src["industry"] != "cross":
                continue
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.get(src["url"])
                    url_hash = hashlib.md5(f"{src['name']}_{datetime.now().isoformat()}".encode()).hexdigest()
                    article = Article(
                        title=f"Data from {src['name']}",
                        content=resp.text[:1000],
                        source_name=src["name"],
                        source_url=src["url"],
                        category=src.get("category", "news"),
                        industry=src["industry"],
                        weight_score=src["weight"],
                        url_hash=url_hash,
                        published_at=datetime.now(timezone.utc)
                    )
                    results.append(article)
            except Exception as e:
                print(f"Failed to fetch {src['name']}: {e}")
        return results
