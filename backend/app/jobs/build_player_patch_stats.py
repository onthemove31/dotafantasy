from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import exp
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.models import Match, MatchPlayer


@dataclass
class PlayerHeroPatchStats:
    account_id: int
    hero_id: int
    games: int
    win_rate: float
    kda: float
    gpm: float
    xpm: float
    fantasy_ppg: float


def exponential_weight(days_since: float, lam: float = 0.03) -> float:
    return float(exp(-lam * days_since))


def compute_player_patch_stats(patch: str, window_days: int, lam: float = 0.03) -> list[PlayerHeroPatchStats]:
    db: Session = SessionLocal()
    cutoff = datetime.utcnow() - timedelta(days=window_days)
    try:
        rows = db.execute(
            select(
                MatchPlayer.account_id,
                MatchPlayer.hero_id,
                MatchPlayer.kills,
                MatchPlayer.deaths,
                MatchPlayer.assists,
                MatchPlayer.gpm,
                MatchPlayer.xpm,
                MatchPlayer.win,
                Match.start_time,
            )
            .join(Match, Match.match_id == MatchPlayer.match_id)
            .where(Match.patch == patch, Match.start_time != None, Match.start_time >= cutoff)
        ).all()
        agg: dict[tuple[int, int], dict[str, float]] = {}
        for (aid, hid, k, d, a, g, x, w, st) in rows:
            if st is None:
                continue
            days = (datetime.utcnow() - st).days
            wgt = exponential_weight(days, lam)
            rec = agg.setdefault((aid, hid), {"picks": 0.0, "wins": 0.0, "k": 0.0, "d": 0.0, "a": 0.0, "g": 0.0, "x": 0.0})
            rec["picks"] += wgt
            rec["wins"] += wgt if w else 0.0
            rec["k"] += wgt * k
            rec["d"] += wgt * d
            rec["a"] += wgt * a
            rec["g"] += wgt * g
            rec["x"] += wgt * x
        out: list[PlayerHeroPatchStats] = []
        for (aid, hid), rec in agg.items():
            picks = rec["picks"]
            win_rate = (rec["wins"] / picks) if picks else 0.0
            kda = ((rec["k"] + rec["a"]) / max(rec["d"], 1.0)) if picks else 0.0
            out.append(
                PlayerHeroPatchStats(
                    account_id=aid,
                    hero_id=hid,
                    games=int(round(picks)),
                    win_rate=win_rate,
                    kda=kda,
                    gpm=rec["g"] / picks if picks else 0.0,
                    xpm=rec["x"] / picks if picks else 0.0,
                    fantasy_ppg=0.0,
                )
            )
        return out
    finally:
        db.close()
