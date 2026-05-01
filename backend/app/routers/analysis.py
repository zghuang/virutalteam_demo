from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.article import Article
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


# ── Request schemas ──────────────────────────────────────────────


class SummarizeRequest(BaseModel):
    text_ids: list[int]


class SentimentRequest(BaseModel):
    text_ids: list[int]


class TrendsRequest(BaseModel):
    timeframe: str = "7d"


class InsightsRequest(BaseModel):
    topic: str
    text_ids: list[int]


# ── Dependency ───────────────────────────────────────────────────


def _fetch_articles(db: Session, text_ids: list[int]) -> list[Article]:
    articles = db.query(Article).filter(Article.id.in_(text_ids)).all()
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found for the given IDs")
    return articles


def _get_service() -> AnalysisService:
    return AnalysisService()


# ── Endpoints ────────────────────────────────────────────────────


@router.post("/summarize")
async def summarize(
    request: SummarizeRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Summarize one or more articles by their IDs."""
    articles = _fetch_articles(db, request.text_ids)
    service = _get_service()

    summaries: dict[str, str] = {}
    for article in articles:
        text = (article.content or article.title or "")
        summaries[str(article.id)] = await service.summarize(text)

    return {"summaries": summaries}


@router.post("/sentiment")
async def sentiment(
    request: SentimentRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Analyze sentiment of one or more articles by their IDs."""
    articles = _fetch_articles(db, request.text_ids)
    service = _get_service()

    results: dict[str, dict[str, Any]] = {}
    for article in articles:
        text = (article.content or article.title or "")
        results[str(article.id)] = await service.analyze_sentiment(text)

    return {"sentiments": results}


@router.post("/trends")
async def trends(
    request: TrendsRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Detect emerging trends from recent articles within the given timeframe."""
    # Simple timeframe parsing: "7d", "14d", "30d"
    days_map = {"7d": 7, "14d": 14, "30d": 30}
    days = days_map.get(request.timeframe, 7)

    from datetime import datetime, timedelta

    cutoff = datetime.utcnow() - timedelta(days=days)
    articles = (
        db.query(Article)
        .filter(Article.created_at >= cutoff)
        .order_by(Article.created_at.desc())
        .limit(50)
        .all()
    )

    titles = [a.title for a in articles if a.title]
    service = _get_service()
    detected = await service.detect_trends(titles)

    return {
        "timeframe": request.timeframe,
        "articles_analyzed": len(titles),
        "trends": detected,
    }


@router.post("/insights")
async def insights(
    request: InsightsRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Extract key insights from articles on a specific topic."""
    articles = _fetch_articles(db, request.text_ids)
    texts = [a.content or a.title or "" for a in articles]
    service = _get_service()

    result = await service.extract_insights(texts)

    return {
        "topic": request.topic,
        "articles_analyzed": len(texts),
        "insights": result,
    }
