from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.article import Article
from app.models.source import Source

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/kpi")
def get_kpi(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Return key performance indicators for the dashboard."""
    total_articles = db.query(func.count(Article.id)).scalar() or 0

    articles_by_industry_rows = (
        db.query(Article.category, func.count(Article.id))
        .filter(Article.category.isnot(None))
        .group_by(Article.category)
        .all()
    )
    articles_by_industry = {
        row[0]: row[1] for row in articles_by_industry_rows
    }

    active_sources = (
        db.query(func.count(Source.id))
        .filter(Source.is_active.is_(True))
        .scalar()
        or 0
    )

    # total_alerts is a placeholder — can be wired to an alerts table later
    total_alerts = 0

    return {
        "total_articles": total_articles,
        "articles_by_industry": articles_by_industry,
        "active_sources": active_sources,
        "total_alerts": total_alerts,
    }


@router.get("/charts")
def get_charts(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Return chart data for the dashboard."""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    volume_rows = (
        db.query(
            func.date_trunc("day", Article.created_at).label("date"),
            func.count(Article.id).label("count"),
        )
        .filter(Article.created_at >= thirty_days_ago)
        .group_by(func.date_trunc("day", Article.created_at))
        .order_by(func.date_trunc("day", Article.created_at))
        .all()
    )
    article_volume = [
        {"date": str(row.date), "count": row.count} for row in volume_rows
    ]

    # Sentiment trend — placeholder returning neutral trend;
    # a real implementation would read from a sentiment analysis table.
    sentiment_trend = {
        "positive": 0,
        "neutral": total_article_count(db),
        "negative": 0,
    }

    return {
        "article_volume": article_volume,
        "sentiment_trend": sentiment_trend,
    }


def total_article_count(db: Session) -> int:
    return db.query(func.count(Article.id)).scalar() or 0
