from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# In-memory alert store (replace with DB model for production)
alerts_db: list[dict] = []
_alert_id_counter: int = 0
_events_db: list[dict] = []


# ── Schemas ──────────────────────────────────────────────────────

class AlertCreate(BaseModel):
    name: str
    keyword: str
    category: Optional[str] = None
    source: Optional[str] = None
    frequency: str = "daily"  # daily | weekly | realtime
    enabled: bool = True
    notify_email: bool = True


class AlertUpdate(BaseModel):
    name: Optional[str] = None
    keyword: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    frequency: Optional[str] = None
    enabled: Optional[bool] = None
    notify_email: Optional[bool] = None


# ── CRUD Endpoints ───────────────────────────────────────────────

@router.get("")
def list_alerts():
    """Get all configured alerts."""
    return {"alerts": alerts_db, "total": len(alerts_db)}


@router.post("")
def create_alert(payload: AlertCreate):
    """Create a new keyword alert."""
    global _alert_id_counter
    _alert_id_counter += 1
    alert = {
        "id": _alert_id_counter,
        "name": payload.name,
        "keyword": payload.keyword,
        "category": payload.category,
        "source": payload.source,
        "frequency": payload.frequency,
        "enabled": payload.enabled,
        "notify_email": payload.notify_email,
        "created_at": datetime.utcnow().isoformat(),
    }
    alerts_db.append(alert)
    return {"alert": alert}


@router.put("/{alert_id}")
def update_alert(alert_id: int, payload: AlertUpdate):
    """Update an existing alert."""
    for alert in alerts_db:
        if alert["id"] == alert_id:
            if payload.name is not None:
                alert["name"] = payload.name
            if payload.keyword is not None:
                alert["keyword"] = payload.keyword
            if payload.category is not None:
                alert["category"] = payload.category
            if payload.source is not None:
                alert["source"] = payload.source
            if payload.frequency is not None:
                alert["frequency"] = payload.frequency
            if payload.enabled is not None:
                alert["enabled"] = payload.enabled
            if payload.notify_email is not None:
                alert["notify_email"] = payload.notify_email
            return {"alert": alert}
    raise HTTPException(status_code=404, detail="Alert not found")


@router.delete("/{alert_id}")
def delete_alert(alert_id: int):
    """Delete an alert."""
    for i, alert in enumerate(alerts_db):
        if alert["id"] == alert_id:
            alerts_db.pop(i)
            return {"deleted": True, "alert_id": alert_id}
    raise HTTPException(status_code=404, detail="Alert not found")


# ── Events Endpoint ──────────────────────────────────────────────

@router.get("/events")
def list_alert_events(
    limit: int = Query(50, ge=1, le=200),
    alert_id: Optional[int] = Query(None),
):
    """Get recent alert-triggered events."""
    events = _events_db
    if alert_id is not None:
        events = [e for e in events if e["alert_id"] == alert_id]
    return {"events": events[:limit], "total": len(events)}
