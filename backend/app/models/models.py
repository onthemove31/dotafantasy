from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Integer, Boolean, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Player(Base):
    __tablename__ = "players"

    account_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    persona_name: Mapped[str | None] = mapped_column(String(120))
    team_name: Mapped[str | None] = mapped_column(String(120))
    last_seen: Mapped[datetime | None] = mapped_column()


class Match(Base):
    __tablename__ = "matches"

    match_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_time: Mapped[datetime | None]
    duration: Mapped[int] = mapped_column(Integer)
    patch: Mapped[str] = mapped_column(String(16), server_default=text("'unknown'"))
    radiant_win: Mapped[bool] = mapped_column(Boolean)


class MatchPlayer(Base):
    __tablename__ = "match_players"
    __table_args__ = (
        UniqueConstraint("match_id", "account_id", name="uix_match_player"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.match_id", ondelete="CASCADE"))
    account_id: Mapped[int] = mapped_column(ForeignKey("players.account_id", ondelete="CASCADE"))

    hero_id: Mapped[int] = mapped_column(Integer)
    kills: Mapped[int] = mapped_column(Integer, default=0)
    deaths: Mapped[int] = mapped_column(Integer, default=0)
    assists: Mapped[int] = mapped_column(Integer, default=0)
    gpm: Mapped[int] = mapped_column(Integer, default=0)
    xpm: Mapped[int] = mapped_column(Integer, default=0)
    lh: Mapped[int] = mapped_column(Integer, default=0)
    dn: Mapped[int] = mapped_column(Integer, default=0)
    damage: Mapped[int] = mapped_column(Integer, default=0)
    stuns: Mapped[float] = mapped_column(default=0.0)
    wards_placed: Mapped[int] = mapped_column(Integer, default=0)
    wards_destroyed: Mapped[int] = mapped_column(Integer, default=0)
    win: Mapped[bool] = mapped_column(Boolean)
