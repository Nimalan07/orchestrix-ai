from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["application"] == "Orchestrix"
    assert data["status"] == "running"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Orchestrix API" in data["service"]


def test_head_endpoints_for_uptime_monitors():
    root_head = client.head("/")
    assert root_head.status_code == 200

    health_head = client.head("/health")
    assert health_head.status_code == 200
