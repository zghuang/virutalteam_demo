from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from datetime import datetime, timedelta, timezone

router = APIRouter(tags=["dashboard"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/dashboard/kpi")
async def get_kpis(db: Session = Depends(get_db)):
    return {
        "total_articles": 1284,
        "articles_by_industry": {"pharma": 520, "lifescience": 380, "semiconductor": 384},
        "active_sources": 14,
        "total_alerts": 8,
    }

@router.get("/api/dashboard/charts")
async def get_charts(db: Session = Depends(get_db)):
    today = datetime.utcnow()
    return {
        "article_volume": [
            {"date": (today - timedelta(days=i)).strftime("%Y-%m-%d"), "count": 10 + (i % 20)}
            for i in range(30)
        ],
        "sentiment_trend": {"positive": 0.45, "neutral": 0.35, "negative": 0.20},
    }

@router.get("/api/dashboard/leadership-summary")
def get_leadership_summary():
    return {
        "total_articles": 1284,
        "active_sources": 42,
        "active_alerts": 17,
        "report_count_today": 9,
        "top_priority_sector": "pharma",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

@router.get("/api/dashboard/source-health")
def get_source_health():
    from datetime import datetime, timezone
    return {
        "healthy_sources": 12,
        "degraded_sources": 2,
        "offline_sources": 1,
        "status": "ok",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
