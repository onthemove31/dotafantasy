from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
import numpy as np

from app.db.session import SessionLocal
from app.models.models import Match, MatchPlayer
from sqlalchemy import select


@dataclass
class FeatureMatrix:
    X: np.ndarray
    y: np.ndarray
    feature_names: list[str]


def build_player_fantasy_regression_dataset(patch: str) -> FeatureMatrix:
    db = SessionLocal()
    try:
        rows = db.execute(
            select(MatchPlayer.kills, MatchPlayer.deaths, MatchPlayer.assists, MatchPlayer.gpm, MatchPlayer.xpm, MatchPlayer.win)
            .join(Match, Match.match_id == MatchPlayer.match_id)
            .where(Match.patch == patch)
        ).all()
        if not rows:
            # Return a tiny synthetic dataset to keep training path testable
            X = np.array([[10, 2, 15, 500, 600, 1], [2, 10, 3, 350, 400, 0]], dtype=float)
        else:
            X = np.array(rows, dtype=float)
        # A simple proxy for fantasy target using default weights
        from app.services.scoring import load_weights

        w = load_weights()
        y = (
            X[:, 0] * w.kill
            + X[:, 1] * w.death
            + X[:, 2] * w.assist
            + X[:, 3] * w.gpm
            + X[:, 4] * w.xpm
            + X[:, 5] * w.win
        )
        feature_names = ["kills", "deaths", "assists", "gpm", "xpm", "win"]
        return FeatureMatrix(X=X, y=y, feature_names=feature_names)
    finally:
        db.close()


def build_team_win_classification_dataset(patch: str) -> FeatureMatrix:
    # Extremely simplified for scaffolding: reuse same features
    ds = build_player_fantasy_regression_dataset(patch)
    # target: win column
    y = ds.X[:, 5]
    X = ds.X[:, :5]
    return FeatureMatrix(X=X, y=y, feature_names=ds.feature_names[:5])
