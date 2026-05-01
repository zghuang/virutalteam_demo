import httpx
import json
from typing import Optional
from app.config import settings

class AnalysisService:
    """AI-powered analysis using LLM API."""
    
    def __init__(self, api_key: str = None, model: str = "deepseek-chat"):
        self.api_key = api_key or "sk-placeholder"
        self.model = model
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    async def _call_llm(self, system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> str:
        """Call the LLM API with prompts."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.3
                }
            )
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    
    async def summarize(self, text: str) -> str:
        """Summarize article into 3 bullet points."""
        if not text or len(text) < 50:
            return "Text too short to summarize."
        return await self._call_llm(
            "You are an expert analyst. Summarize concisely.",
            f"Summarize this in 3 bullet points (key facts, companies, impact):\n\n{text[:3000]}"
        )
    
    async def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment of text."""
        resp = await self._call_llm(
            "You are a sentiment analyst. Return ONLY valid JSON.",
            f"Analyze sentiment. Return JSON: {{\"sentiment\": \"positive/negative/neutral\", \"score\": 0.0-1.0}}\n\nText: {text[:2000]}"
        )
        try:
            return json.loads(resp)
        except:
            return {"sentiment": "neutral", "score": 0.5}
    
    async def detect_trends(self, titles: list[str]) -> list:
        """Detect emerging trends from article titles."""
        titles_text = "\n".join(f"- {t}" for t in titles[:20])
        resp = await self._call_llm(
            "You are a trend analyst. Return ONLY valid JSON array.",
            f"Analyze these article titles for emerging trends. Return JSON array: [{{\"trend\": \"...\", \"count\": N, \"keywords\": [...]}}]\n\n{titles_text}"
        )
        try:
            result = json.loads(resp)
            return result if isinstance(result, list) else []
        except:
            return []
    
    async def extract_insights(self, articles_texts: list[str]) -> list:
        """Extract key insights from articles."""
        combined = "\n---\n".join(a[:500] for a in articles_texts[:5])
        resp = await self._call_llm(
            "You are an intelligence analyst. Extract actionable insights.",
            f"Extract key insights. Return JSON array: [{{\"insight\": \"...\", \"importance\": 1-5, \"related_companies\": [...]}}]\n\n{combined}"
        )
        try:
            return json.loads(resp)
        except:
            return [{"insight": "Analysis unavailable", "importance": 1, "related_companies": []}]
    
    async def generate_report(self, topic: str, articles_texts: list[str]) -> dict:
        """Generate comprehensive intelligence report on a topic."""
        combined = "\n---\n".join(a[:500] for a in articles_texts[:8])
        resp = await self._call_llm(
            "You are a senior analyst generating executive reports.",
            f"Generate a report on: {topic}\n\nBased on these articles:\n{combined}\n\nReturn JSON: {{\"executive_summary\": \"...\", \"key_findings\": [...], \"recommendations\": [...], \"confidence\": 0.0-1.0}}"
        )
        try:
            return json.loads(resp)
        except:
            return {"executive_summary": "Report generation pending.", "key_findings": [], "recommendations": [], "confidence": 0.0}
