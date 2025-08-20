from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone

router = APIRouter(prefix="/heroes", tags=["heroes"])


class HeroPatchStatsResponse(BaseModel):
    hero_id: int
    patch: str
    pick_rate: float
    win_rate: float
    avg_kda: float
    avg_gpm: float
    avg_xpm: float
    data_timestamp: str


@router.get("/{hero_id}/patch-stats")
async def hero_patch_stats(hero_id: int, patch: str) -> dict:
    # Placeholder: would query precomputed stats
    return {
        "hero_id": hero_id,
        "patch": patch,
        "pick_rate": 0.05,
        "win_rate": 0.51,
        "avg_kda": 3.2,
        "avg_gpm": 480.0,
        "avg_xpm": 540.0,
        "data_timestamp": datetime.now(timezone.utc).isoformat(),
    }
