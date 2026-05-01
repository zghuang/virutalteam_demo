from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from app.database import Base, SessionLocal

OFFICIAL_SOURCES = [
    {
        "name": "openFDA",
        "url": "https://api.fda.gov",
        "weight_score": 10,
        "category": "regulatory",
        "is_active": True,
    },
    {
        "name": "ClinicalTrials.gov",
        "url": "https://clinicaltrials.gov",
        "weight_score": 10,
        "category": "clinical",
        "is_active": True,
    },
    {
        "name": "SEC EDGAR",
        "url": "https://www.sec.gov/cgi-bin/browse-edgar",
        "weight_score": 10,
        "category": "financial",
        "is_active": True,
    },
    {
        "name": "PubMed",
        "url": "https://pubmed.ncbi.nlm.nih.gov",
        "weight_score": 10,
        "category": "research",
        "is_active": True,
    },
    {
        "name": "Drugs.com",
        "url": "https://www.drugs.com",
        "weight_score": 10,
        "category": "pharma",
        "is_active": True,
    },
]


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    url = Column(String, nullable=False)
    weight_score = Column(Integer, default=10)
    category = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def seed_official_sources(db: SessionLocal):
    existing = db.query(Source).all()
    if existing:
        return
    for source_data in OFFICIAL_SOURCES:
        source = Source(**source_data)
        db.add(source)
    db.commit()
