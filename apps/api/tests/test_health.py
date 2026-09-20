"""
Smoke test for the DevOps scaffold itself (proves pytest + FastAPI TestClient
wiring works in the container). Backend Architect: add feature test modules
alongside this one, e.g. test_events.py, test_temples.py, etc. (BE-13).
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "service" in body
