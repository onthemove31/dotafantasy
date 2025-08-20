from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, timezone
import random

router = APIRouter(prefix="/simulate", tags=["simulate"])


class PlayerInput(BaseModel):
    account_id: int
    name: str


class TeamInput(BaseModel):
    players: list[PlayerInput]
    heroes: list[int]


class DraftSimRequest(BaseModel):
    tournament: str
    patch: str
    teams: dict[str, TeamInput]
    options: dict | None = None


@router.post("/draft")
async def simulate_draft(req: DraftSimRequest) -> dict:
    seed = (req.options or {}).get("seed", 42)
    rnd = random.Random(seed)
    # Simple deterministic per-player fantasy baseline
    results = {}
    for side, team in req.teams.items():
        results[side] = {
            "players": [
                {"account_id": p.account_id, "name": p.name, "expected_fantasy_ppg": 20 + rnd.random() * 10}
                for p in team.players
            ]
        }
    win_prob = 0.5 + (rnd.random() - 0.5) * 0.1
    return {
        "results": results,
        "team_win_probability": {"A": win_prob, "B": 1 - win_prob},
        "patch": req.patch,
        "data_timestamp": datetime.now(timezone.utc).isoformat(),
    }
