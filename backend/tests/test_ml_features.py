from __future__ import annotations

import numpy as np

from app.ml.features import build_player_fantasy_regression_dataset, build_team_win_classification_dataset


def test_feature_shapes_synthetic():
    ds1 = build_player_fantasy_regression_dataset("7.37b")
    assert ds1.X.ndim == 2 and ds1.y.ndim == 1
    assert ds1.X.shape[1] == 6
    ds2 = build_team_win_classification_dataset("7.37b")
    assert ds2.X.shape[1] == 5
