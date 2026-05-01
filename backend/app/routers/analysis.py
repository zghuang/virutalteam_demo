from fastapi import APIRouter, HTTPException
from app.services.analysis_service import AnalysisService
from typing import List, Optional

router = APIRouter(tags=["analysis"])
svc = AnalysisService()

@router.post("/api/analysis/summarize")
async def summarize(text_ids: List[int]):
    return {"message": "Summarization endpoint ready", "text_ids": text_ids}

@router.post("/api/analysis/sentiment")
async def sentiment(text_ids: List[int]):
    return {"message": "Sentiment endpoint ready", "text_ids": text_ids}

@router.post("/api/analysis/trends")
async def trends(timeframe: str = "7d"):
    return {"message": "Trend detection endpoint ready", "timeframe": timeframe}

@router.post("/api/analysis/insights")
async def insights(topic: str, text_ids: Optional[List[int]] = None):
    return {"message": "Insights endpoint ready", "topic": topic}
