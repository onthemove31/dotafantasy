from __future__ import annotations

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_healthz():
    r = client.get('/healthz')
    assert r.status_code == 200 and r.json() == {"status": "ok"}


def test_simulate_draft():
    payload = {
        "tournament": "Sample Major",
        "patch": "7.37b",
        "teams": {
            "A": {"players": [{"account_id": 137193239, "name": "Miracle-"}], "heroes": [13, 8, 99, 1, 110]},
            "B": {"players": [{"account_id": 12345, "name": "Nisha"}], "heroes": [74, 51, 7, 92, 126]},
        },
        "options": {"seed": 42},
    }
    r = client.post('/simulate/draft', json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["patch"] == "7.37b"
    assert "results" in data and "team_win_probability" in data
