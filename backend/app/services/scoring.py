from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
import math
import yaml

from app.db.session import SessionLocal
from app.models.models import Match, MatchPlayer
from sqlalchemy import select


@dataclass(frozen=True)
class Weights:
    kill: float
    death: float
    assist: float
    gpm: float
    xpm: float
    wards_placed: float
    wards_destroyed: float
    stuns: float
    win: float


def load_weights(path: Path | None = None) -> Weights:
    if path is None:
        path = Path(__file__).resolve().parents[1] / "config" / "scoring.yaml"
    data = yaml.safe_load(path.read_text())
    return Weights(**data)


def score_match_row(row: Mapping[str, float] | MatchPlayer, weights: Weights | None = None) -> float:
    if weights is None:
        weights = load_weights()
    # Row can be a dict-like or ORM object
    def g(name: str, default: float = 0.0) -> float:
        if isinstance(row, MatchPlayer):
            return float(getattr(row, name, default) or 0.0)
        return float(row.get(name, default) or 0.0)  # type: ignore[attr-defined]

    score = 0.0
    score += g("kills") * weights.kill
    score += g("deaths") * weights.death
    score += g("assists") * weights.assist
    score += g("gpm") * weights.gpm
    score += g("xpm") * weights.xpm
    score += g("wards_placed") * weights.wards_placed
    score += g("wards_destroyed") * weights.wards_destroyed
    score += g("stuns") * weights.stuns
    score += (1.0 if g("win") else 0.0) * weights.win
    return float(score)


def compute_fantasy_ppg_for_player(account_id: int, patch: str, window_days: int = 60, decay_lambda: float = 0.03) -> float:
    from datetime import datetime, timedelta

    db = SessionLocal()
    try:
        rows = db.execute(
            select(MatchPlayer, Match)
            .join(Match, Match.match_id == MatchPlayer.match_id)
            .where(MatchPlayer.account_id == account_id, Match.patch == patch)
        ).all()
        if not rows:
            return 0.0
        now = datetime.utcnow()
        numerator = 0.0
        denom = 0.0
        w = load_weights()
        for mp, m in rows:
            if m.start_time is None:
                continue
            days = (now - m.start_time).days
            if days > window_days:
                continue
            wt = math.exp(-decay_lambda * days)
            numerator += wt * score_match_row(mp, w)
            denom += wt
        return float(numerator / denom) if denom > 0 else 0.0
    finally:
        db.close()
