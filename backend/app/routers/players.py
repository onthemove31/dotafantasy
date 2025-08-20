from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime, timezone

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.models import Player

router = APIRouter(prefix="/players", tags=["players"])


class PlayerSearchResult(BaseModel):
    account_id: int
    persona_name: str | None = None
    team_name: str | None = None


@router.get("/search")
async def search_players(q: str) -> dict:
    db = SessionLocal()
    try:
        ql = f"%{q.lower()}%"
        rows = db.execute(
            select(Player).where(
                (Player.persona_name.ilike(ql)) | (Player.team_name.ilike(ql))
            ).limit(20)
        ).scalars().all()
        results = [PlayerSearchResult(account_id=p.account_id, persona_name=p.persona_name, team_name=p.team_name).model_dump() for p in rows]
        return {"results": results, "patch": "unknown", "data_timestamp": datetime.now(timezone.utc).isoformat()}
    finally:
        db.close()


@router.get("/{account_id}/summary")
async def player_summary(account_id: int, patch: str) -> dict:
    # Minimal placeholder; will be expanded in later tickets
    db = SessionLocal()
    try:
        p = db.get(Player, account_id)
        if not p:
            raise HTTPException(status_code=404, detail="Player not found")
        return {
            "account_id": account_id,
            "persona_name": p.persona_name,
            "team_name": p.team_name,
            "patch": patch,
            "data_timestamp": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        db.close()
