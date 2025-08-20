from __future__ import annotations

import os
from typing import Generator, TypeAlias

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dota_fd.db")


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)

SessionType: TypeAlias = Session


def get_engine():
    return engine


def get_session() -> Generator[SessionType, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
