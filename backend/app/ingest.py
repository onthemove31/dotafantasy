from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
from typing import Set

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clients.opendota import OpenDotaClient
from app.db.session import Base, engine, SessionLocal
from app.models.models import Player, Match, MatchPlayer
from app.utils.patches import normalize_patch, infer_patch_from_time


def _utc_from_unix(ts: int | None) -> datetime | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc)


async def ingest(players: str = "top", limit: int = 25) -> None:
    # Ensure tables exist (dev convenience; in prod use Alembic)
    Base.metadata.create_all(bind=engine)
    async with OpenDotaClient() as od:
        pro_players = await od.get_pro_players()
        pro_players = [p for p in pro_players if getattr(p, "account_id", None)]
        pro_players = pro_players[:limit]

        match_ids: Set[int] = set()
        for p in pro_players:
            matches = await od.get_player_matches(p.account_id, limit=limit)
            for m in matches:
                match_ids.add(m.match_id)

        db: Session = SessionLocal()
        try:
            for mid in list(match_ids):
                details = await od.get_match_details(mid)

                # Upsert Match
                mobj = db.get(Match, details.match_id)
                if not mobj:
                    mobj = Match(
                        match_id=details.match_id,
                        start_time=_utc_from_unix(details.start_time),
                        duration=details.duration,
                        patch=
                            normalize_patch(details.patch)
                            if details.patch
                            else infer_patch_from_time(
                                _utc_from_unix(details.start_time) or datetime.now(timezone.utc)
                            ),
                        radiant_win=details.radiant_win,
                    )
                    db.add(mobj)
                else:
                    mobj.start_time = _utc_from_unix(details.start_time)
                    mobj.duration = details.duration
                    if details.patch:
                        mobj.patch = normalize_patch(details.patch)
                    mobj.radiant_win = details.radiant_win

                # Upsert players and match-player rows
                for pl in details.players:
                    if pl.account_id is None:
                        continue
                    pobj = db.get(Player, pl.account_id)
                    if not pobj:
                        pobj = Player(account_id=pl.account_id)
                        db.add(pobj)

                    existing = db.execute(
                        select(MatchPlayer).where(
                            MatchPlayer.match_id == details.match_id,
                            MatchPlayer.account_id == pl.account_id,
                        )
                    ).scalar_one_or_none()
                    if existing:
                        mp = existing
                    else:
                        mp = MatchPlayer(match_id=details.match_id, account_id=pl.account_id)
                        db.add(mp)

                    mp.hero_id = pl.hero_id
                    mp.kills = pl.kills
                    mp.deaths = pl.deaths
                    mp.assists = pl.assists
                    mp.gpm = getattr(pl, "gold_per_min", 0)
                    mp.xpm = getattr(pl, "xp_per_min", 0)
                    mp.lh = getattr(pl, "last_hits", 0)
                    mp.dn = getattr(pl, "denies", 0)
                    mp.damage = getattr(pl, "hero_damage", 0)
                    mp.stuns = float(getattr(pl, "stuns", 0.0) or 0.0)
                    wards_placed = (getattr(pl, "obs_placed", 0) or 0) + (getattr(pl, "sen_placed", 0) or 0)
                    wards_destroyed = (getattr(pl, "obs_destroyed", 0) or 0) + (getattr(pl, "sen_destroyed", 0) or 0)
                    mp.wards_placed = int(wards_placed)
                    mp.wards_destroyed = int(wards_destroyed)
                    is_radiant = pl.player_slot < 128
                    mp.win = is_radiant == details.radiant_win

                db.commit()
        finally:
            db.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--players", default="top")
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args()
    asyncio.run(ingest(args.players, args.limit))


if __name__ == "__main__":
    main()
