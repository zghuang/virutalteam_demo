import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime, timezone

client = TestClient(app)

class TestDashboardSourceHealth:
    def test_source_health_structure_and_types(self):
        resp = client.get("/api/dashboard/source-health")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["healthy_sources"], int)
        assert isinstance(data["degraded_sources"], int)
        assert isinstance(data["offline_sources"], int)
        assert data["status"] == "ok"
        assert isinstance(data["checked_at"], str)
        # Verify ISO 8601 parseable and timezone-aware
        dt = datetime.fromisoformat(data["checked_at"])
        assert dt.tzinfo is not None
