import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import hashlib
from app.models.article import Article
from app.database import SessionLocal

class SemiconductorIngestionService:
    """Specialized ingestion for semiconductor industry data."""
    
    PATENT_SOURCES = [
        {"name": "USPTO", "url": "https://developer.uspto.gov/ds-api/patent/", "weight": 9},
        {"name": "Google Patents", "url": "https://patents.google.com/api/", "weight": 7},
    ]
    
    COMPANY_NEWS = [
        {"name": "Intel News", "url": "https://newsroom.intel.com/feed/", "weight": 9},
        {"name": "TSMC News", "url": "https://www.tsmc.com/static/newsRss.htm", "weight": 9},
        {"name": "Samsung News", "url": "https://news.samsung.com/global/rss", "weight": 8},
    ]
    
    async def fetch_patents(self, query="semiconductor", limit=5):
        results = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                url = f"https://developer.uspto.gov/ds-api/patent/search?q={query}&limit={limit}"
                resp = await client.get(url)
                url_hash = hashlib.md5(f"patent_{datetime.now().isoformat()}".encode()).hexdigest()
                article = Article(
                    title=f"Patent search: {query}",
                    content=resp.text[:2000],
                    source_name="USPTO",
                    source_url=url,
                    category="patents",
                    industry="semiconductor",
                    weight_score=9,
                    url_hash=url_hash,
                    published_at=datetime.now(timezone.utc)
                )
                results.append(article)
            except Exception as e:
                print(f"Patent fetch failed: {e}")
        return results
    
    async def fetch_company_news(self):
        results = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for src in self.COMPANY_NEWS:
                try:
                    resp = await client.get(src["url"])
                    soup = BeautifulSoup(resp.text, 'lxml')
                    items = soup.find_all('item')[:3] if soup.find_all('item') else []
                    for item in items:
                        title = item.find('title').text if item.find('title') else f"News from {src['name']}"
                        url_hash = hashlib.md5(f"{src['name']}_{title}".encode()).hexdigest()
                        article = Article(
                            title=title,
                            content=item.find('description').text[:1000] if item.find('description') else "",
                            source_name=src["name"],
                            source_url=src["url"],
                            category="company_news",
                            industry="semiconductor",
                            weight_score=src["weight"],
                            url_hash=url_hash,
                            published_at=datetime.now(timezone.utc)
                        )
                        results.append(article)
                except Exception as e:
                    print(f"Failed {src['name']}: {e}")
        return results
