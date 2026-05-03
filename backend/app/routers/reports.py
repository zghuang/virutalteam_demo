from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel

router = APIRouter(prefix="/api/reports", tags=["reports"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# In-memory report store (replace with DB + async generation for production)
reports_db: list[dict] = []
_report_id_counter: int = 0


# ── Schemas ──────────────────────────────────────────────────────

class ReportGenerateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    report_type: str = "summary"  # summary | trend | anomaly | full
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    filters: Optional[dict] = None


# ── Endpoints ────────────────────────────────────────────────────

@router.get("")
def list_reports(
    report_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    """List generated reports."""
    reports = reports_db
    if report_type:
        reports = [r for r in reports if r["report_type"] == report_type]
    reports = sorted(reports, key=lambda r: r["created_at"], reverse=True)
    return {"reports": reports[:limit], "total": len(reports)}


@router.post("/generate")
def generate_report(payload: ReportGenerateRequest):
    """Generate a new report (synchronous stub — real impl would be async)."""
    global _report_id_counter
    _report_id_counter += 1

    report = {
        "id": _report_id_counter,
        "title": payload.title,
        "description": payload.description,
        "report_type": payload.report_type,
        "date_from": payload.date_from,
        "date_to": payload.date_to,
        "filters": payload.filters or {},
        "status": "completed",
        "created_at": datetime.utcnow().isoformat(),
        "content": f"# {payload.title}\n\nReport generated at {datetime.utcnow().isoformat()}.\n\n*Type: {payload.report_type}*\n\nThis is a stub report. Full content generation is coming soon.",
    }
    reports_db.append(report)
    return {"report": report}


@router.get("/status")
def get_reports_status():
    """Get report status summary."""
    total = len(reports_db)
    completed = sum(1 for r in reports_db if r.get("status") == "completed")
    pending = sum(1 for r in reports_db if r.get("status") == "pending")
    return {
        "total_reports": total,
        "completed_reports": completed,
        "pending_reports": pending,
        "status": "ok",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/{report_id}")
def get_report(report_id: int):
    """Get a single report by ID."""
    for report in reports_db:
        if report["id"] == report_id:
            return {"report": report}
    raise HTTPException(status_code=404, detail="Report not found")
