from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.database import Base


class FinancialData(Base):
    __tablename__ = "financial_data"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    ticker = Column(String, nullable=False, index=True)
    data_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    currency = Column(String, nullable=True)
    period = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
