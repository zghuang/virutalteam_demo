from sqlalchemy import Column, Integer, String, Text, DateTime, func
from datetime import datetime

from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    source_name = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    category = Column(String, nullable=True)
    weight_score = Column(Integer, nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    url_hash = Column(String, unique=True, index=True, nullable=False)
