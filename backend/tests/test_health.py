from fastapi.testclient import TestClient
from app.main import app


def test_healthz_ok():
    client = TestClient(app)
    r = client.get("/healthz")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
