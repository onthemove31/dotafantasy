from __future__ import annotations

from app.services.scoring import load_weights, score_match_row


def test_score_match_row_basic(tmp_path):
    # Use default weights
    w = load_weights()
    row = {
        "kills": 10,
        "deaths": 2,
        "assists": 15,
        "gpm": 500,
        "xpm": 600,
        "wards_placed": 3,
        "wards_destroyed": 2,
        "stuns": 12.5,
        "win": 1,
    }
    score = score_match_row(row, w)
    # Simple deterministic total
    expected = (
        10 * w.kill
        + 2 * w.death
        + 15 * w.assist
        + 500 * w.gpm
        + 600 * w.xpm
        + 3 * w.wards_placed
        + 2 * w.wards_destroyed
        + 12.5 * w.stuns
        + 1 * w.win
    )
    assert abs(score - expected) < 1e-6
