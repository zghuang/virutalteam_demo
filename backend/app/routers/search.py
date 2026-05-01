from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import SessionLocal
from app.models.article import Article
from app.models.financial_data import FinancialData
from app.services.embedding_service import get_embedding
from app.services.milvus_service import MilvusService
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/search", tags=["search"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def search_articles(
    q: str = Query(..., min_length=1),
    category: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Article).filter(
        or_(
            Article.title.ilike(f"%{q}%"),
            Article.content.ilike(f"%{q}%"),
        )
    )

    if category:
        query = query.filter(Article.category == category)
    if date_from:
        query = query.filter(Article.published_at >= date_from)
    if date_to:
        query = query.filter(Article.published_at <= date_to)

    articles = query.order_by(Article.published_at.desc()).all()

    results = []
    for a in articles:
        content_preview = a.content[:200] if a.content else ""
        results.append({
            "id": a.id,
            "title": a.title,
            "content": content_preview,
            "source_name": a.source_name,
            "category": a.category,
            "source_weight": a.weight_score,
            "published_at": a.published_at,
        })

    return {"results": results, "total": len(results)}


@router.get("/semantic")
def search_semantic(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
):
    embedding = get_embedding(q)
    milvus = MilvusService()
    matches = milvus.search_similar(embedding, limit=limit)

    results = []
    for match in matches:
        results.append({
            "id": match["id"],
            "text": match["text"],
            "distance": match["distance"],
        })

    return {"results": results, "total": len(results)}


@router.get("/financial")
def search_financial(
    q: Optional[str] = Query(None),
    ticker: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(FinancialData)

    if q:
        query = query.filter(FinancialData.company_name.ilike(f"%{q}%"))
    if ticker:
        query = query.filter(FinancialData.ticker == ticker.upper())
    if date_from:
        query = query.filter(FinancialData.published_at >= date_from)
    if date_to:
        query = query.filter(FinancialData.published_at <= date_to)

    records = query.order_by(FinancialData.published_at.desc()).all()

    results = []
    for r in records:
        results.append({
            "id": r.id,
            "company_name": r.company_name,
            "ticker": r.ticker,
            "data_type": r.data_type,
            "value": r.value,
            "currency": r.currency,
            "period": r.period,
            "published_at": r.published_at,
        })

    return {"results": results, "total": len(results)}
