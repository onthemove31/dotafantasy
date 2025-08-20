from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, timezone

from app.services.scoring import compute_fantasy_ppg_for_player

router = APIRouter(prefix="/predict", tags=["predict"])


class PlayerPredictRequest(BaseModel):
    account_id: int
    patch: str
    context: dict | None = None


@router.post("/player")
async def predict_player(req: PlayerPredictRequest) -> dict:
    ppg = compute_fantasy_ppg_for_player(req.account_id, req.patch)
    return {
        "expected_fantasy_ppg": ppg,
        "ci": [ppg - 2.0, ppg + 2.0],
        "model_version": "0.1.0",
        "patch": req.patch,
        "data_freshness": datetime.now(timezone.utc).isoformat(),
    }


class TeamPredictRequest(BaseModel):
    team_a: list[int] | None = None
    team_b: list[int] | None = None
    patch: str


@router.post("/team")
async def predict_team(req: TeamPredictRequest) -> dict:
    # Placeholder deterministic value
    prob = 0.5
    return {
        "win_probability": prob,
        "feature_breakdown": {"recent_form": 0.1, "hero_matchups": -0.05},
        "model_version": "0.1.0",
        "patch": req.patch,
        "data_freshness": datetime.now(timezone.utc).isoformat(),
    }
