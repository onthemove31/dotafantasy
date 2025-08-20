from __future__ import annotations

import asyncio
from sqlalchemy import text, select
from sqlalchemy.orm import Session

from app.ingest import ingest
from app.db.session import Base, engine, SessionLocal
from app.models.models import MatchPlayer


def setup_function() -> None:
    # Recreate schema for test (SQLite)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def count_match_players(db: Session) -> int:
    return db.execute(select(MatchPlayer)).unique().scalars().count()  # type: ignore[attr-defined]


def test_ingest_twice_no_duplicates(monkeypatch):
    # Monkeypatch OpenDota client network with a deterministic small dataset
    from app.clients.opendota import OpenDotaClient, ProPlayer, PlayerMatch, MatchDetails, MatchPlayerDetails

    async def fake_get_pro_players(self):  # type: ignore[no-redef]
        return [ProPlayer(account_id=1, personaname="p1"), ProPlayer(account_id=2, personaname="p2")]

    async def fake_get_player_matches(self, account_id: int, limit: int = 50):  # type: ignore[no-redef]
        return [PlayerMatch(match_id=100), PlayerMatch(match_id=101)]

    async def fake_get_match_details(self, match_id: int):  # type: ignore[no-redef]
        return MatchDetails(
            match_id=match_id,
            start_time=1,
            duration=3000,
            patch="7.37b",
            radiant_win=True,
            players=[
                MatchPlayerDetails(account_id=1, player_slot=0, hero_id=1, kills=10, deaths=2, assists=5),
                MatchPlayerDetails(account_id=2, player_slot=129, hero_id=2, kills=2, deaths=10, assists=1),
            ],
        )

    monkeypatch.setattr(OpenDotaClient, "get_pro_players", fake_get_pro_players)
    monkeypatch.setattr(OpenDotaClient, "get_player_matches", fake_get_player_matches)
    monkeypatch.setattr(OpenDotaClient, "get_match_details", fake_get_match_details)

    # Run ingest twice
    asyncio.run(ingest(limit=2))
    db = SessionLocal()
    try:
        first = db.execute(select(MatchPlayer)).scalars().all()
    finally:
        db.close()

    asyncio.run(ingest(limit=2))

    db = SessionLocal()
    try:
        second = db.execute(select(MatchPlayer)).scalars().all()
    finally:
        db.close()

    assert len(first) == len(second)
