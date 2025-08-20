from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import exp
from typing import Iterable

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.models import Match, MatchPlayer


@dataclass
class HeroPatchStats:
    hero_id: int
    pick_rate: float
    win_rate: float
    avg_kda: float
    avg_gpm: float
    avg_xpm: float


def exponential_weight(days_since: float, lam: float = 0.03) -> float:
    return float(exp(-lam * days_since))


def compute_hero_patch_stats(patch: str, window_days: int, lam: float = 0.03) -> list[HeroPatchStats]:
    db: Session = SessionLocal()
    cutoff = datetime.utcnow() - timedelta(days=window_days)
    try:
        rows = db.execute(
            select(
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
        # Aggregate in Python with recency weights for simplicity
        agg: dict[int, dict[str, float]] = {}
        for (hero_id, k, d, a, g, x, w, st) in rows:
            if st is None:
                continue
            days = (datetime.utcnow() - st).days
            wgt = exponential_weight(days, lam)
            rec = agg.setdefault(hero_id, {"picks": 0.0, "wins": 0.0, "k": 0.0, "d": 0.0, "a": 0.0, "g": 0.0, "x": 0.0})
            rec["picks"] += wgt
            rec["wins"] += wgt if w else 0.0
            rec["k"] += wgt * k
            rec["d"] += wgt * d
            rec["a"] += wgt * a
            rec["g"] += wgt * g
            rec["x"] += wgt * x
        out: list[HeroPatchStats] = []
        total_picks = sum(v["picks"] for v in agg.values()) or 1.0
        for hid, rec in agg.items():
            picks = rec["picks"]
            win_rate = (rec["wins"] / picks) if picks else 0.0
            avg_kda = ((rec["k"] + rec["a"]) / max(rec["d"], 1.0)) if picks else 0.0
            out.append(
                HeroPatchStats(
                    hero_id=hid,
                    pick_rate=picks / total_picks,
                    win_rate=win_rate,
                    avg_kda=avg_kda,
                    avg_gpm=rec["g"] / picks if picks else 0.0,
                    avg_xpm=rec["x"] / picks if picks else 0.0,
                )
            )
        return out
    finally:
        db.close()
