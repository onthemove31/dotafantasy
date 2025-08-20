from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.db.session import Base, engine, SessionLocal
from app.models.models import Match, MatchPlayer, Player
from app.jobs.build_hero_patch_stats import compute_hero_patch_stats
from app.jobs.build_player_patch_stats import compute_player_patch_stats


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Insert synthetic data
        db.add(Player(account_id=1))
        db.add(Player(account_id=2))
        now = datetime.now(timezone.utc)
        m1 = Match(match_id=1, start_time=now - timedelta(days=1), duration=3000, patch="7.37b", radiant_win=True)
        m2 = Match(match_id=2, start_time=now - timedelta(days=5), duration=2900, patch="7.37b", radiant_win=False)
        db.add_all([m1, m2])
        db.flush()
        db.add_all(
            [
                MatchPlayer(match_id=1, account_id=1, hero_id=1, kills=10, deaths=2, assists=8, gpm=500, xpm=600, win=True),
                MatchPlayer(match_id=1, account_id=2, hero_id=2, kills=2, deaths=10, assists=3, gpm=350, xpm=400, win=False),
                MatchPlayer(match_id=2, account_id=1, hero_id=1, kills=6, deaths=4, assists=7, gpm=480, xpm=550, win=False),
                MatchPlayer(match_id=2, account_id=2, hero_id=2, kills=7, deaths=3, assists=5, gpm=470, xpm=520, win=True),
            ]
        )
        db.commit()
    finally:
        db.close()


def test_hero_stats_basic():
    res = compute_hero_patch_stats("7.37b", window_days=60)
    # Should compute for 2 heroes
    ids = {r.hero_id for r in res}
    assert ids == {1, 2}


def test_player_stats_basic():
    res = compute_player_patch_stats("7.37b", window_days=60)
    keys = {(r.account_id, r.hero_id) for r in res}
    assert keys == {(1, 1), (2, 2)}
