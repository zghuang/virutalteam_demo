from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.database import SessionLocal
from app.models.source import Source


router = APIRouter(prefix="/api/sources", tags=["sources"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SourceCreate(BaseModel):
    name: str
    url: str
    weight_score: int = 10
    category: Optional[str] = None
    is_active: bool = True


class SourceUpdate(BaseModel):
    weight_score: Optional[int] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class SourceResponse(BaseModel):
    id: int
    name: str
    url: str
    weight_score: int
    category: Optional[str]
    is_active: bool
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("", response_model=list[SourceResponse])
def list_sources(db: Session = Depends(get_db)):
    sources = (
        db.query(Source)
        .order_by(Source.weight_score.desc())
        .all()
    )
    result = []
    for s in sources:
        result.append({
            "id": s.id,
            "name": s.name,
            "url": s.url,
            "weight_score": s.weight_score,
            "category": s.category,
            "is_active": s.is_active,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        })
    return result


@router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
def create_source(request: SourceCreate, db: Session = Depends(get_db)):
    existing = db.query(Source).filter(Source.name == request.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Source with this name already exists",
        )

    source = Source(
        name=request.name,
        url=request.url,
        weight_score=request.weight_score,
        category=request.category,
        is_active=request.is_active,
    )
    db.add(source)
    db.commit()
    db.refresh(source)

    return {
        "id": source.id,
        "name": source.name,
        "url": source.url,
        "weight_score": source.weight_score,
        "category": source.category,
        "is_active": source.is_active,
        "created_at": source.created_at.isoformat() if source.created_at else None,
    }


@router.put("/{source_id}", response_model=SourceResponse)
def update_source(source_id: int, request: SourceUpdate, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found",
        )

    if request.weight_score is not None:
        source.weight_score = request.weight_score
    if request.category is not None:
        source.category = request.category
    if request.is_active is not None:
        source.is_active = request.is_active

    db.commit()
    db.refresh(source)

    return {
        "id": source.id,
        "name": source.name,
        "url": source.url,
        "weight_score": source.weight_score,
        "category": source.category,
        "is_active": source.is_active,
        "created_at": source.created_at.isoformat() if source.created_at else None,
    }
