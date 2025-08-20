from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.clients.opendota import OpenDotaClient
from app.db.session import Base, engine, SessionLocal
from app.models.models import Player, Match, MatchPlayer


async def ingest(players: str = "top", limit: int = 25) -> None:
    async with OpenDotaClient() as None:  # type: ignore[attr-defined]
        pass


async def ingest_main(players: str, limit: int) -> None:
    # very minimal placeholder to satisfy F3 ticket scaffolding; full logic will follow in F3
    # ensure tables exist for now (SQLite dev)
    Base.metadata.create_all(bind=engine)
    print("Ingestion scaffolding ready (F3 to be completed). players=", players, "limit=", limit)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--players", default="top")
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args()
    asyncio.run(ingest_main(args.players, args.limit))


if __name__ == "__main__":
    main()
