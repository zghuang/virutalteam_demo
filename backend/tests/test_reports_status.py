from fastapi.testclient import TestClient
from app.main import app
from app.routers.reports import reports_db

client = TestClient(app)


def setup_function():
    reports_db.clear()


def test_status_empty():
    resp = client.get("/api/reports/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_reports"] == 0
    assert data["completed_reports"] == 0
    assert data["pending_reports"] == 0
    assert data["status"] == "ok"
    assert "generated_at" in data


def test_status_some_completed():
    reports_db.extend([
        {"id": 1, "status": "completed"},
        {"id": 2, "status": "completed"},
    ])
    resp = client.get("/api/reports/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_reports"] == 2
    assert data["completed_reports"] == 2
    assert data["pending_reports"] == 0


def test_status_some_pending():
    reports_db.extend([
        {"id": 1, "status": "pending"},
        {"id": 2, "status": "completed"},
        {"id": 3, "status": "pending"},
    ])
    resp = client.get("/api/reports/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_reports"] == 3
    assert data["completed_reports"] == 1
    assert data["pending_reports"] == 2


def test_generated_at_iso8601():
    resp = client.get("/api/reports/status")
    data = resp.json()
    assert "T" in data["generated_at"]
    assert data["generated_at"].endswith("+00:00") or "Z" in data["generated_at"]


def test_status_field_ok():
    resp = client.get("/api/reports/status")
    data = resp.json()
    assert data["status"] == "ok"
