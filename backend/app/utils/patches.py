from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Tuple
import os

# Curated patch releases (UTC)
_PATCH_DATES: List[Tuple[str, datetime]] = [
    ("7.32", datetime(2022, 8, 23, 0, 0, tzinfo=timezone.utc)),
    ("7.32d", datetime(2023, 1, 12, 0, 0, tzinfo=timezone.utc)),
    ("7.33", datetime(2023, 4, 20, 0, 0, tzinfo=timezone.utc)),
    ("7.34", datetime(2023, 8, 8, 0, 0, tzinfo=timezone.utc)),
    ("7.34c", datetime(2023, 9, 28, 0, 0, tzinfo=timezone.utc)),
    ("7.35", datetime(2023, 12, 14, 0, 0, tzinfo=timezone.utc)),
    ("7.36", datetime(2024, 5, 23, 0, 0, tzinfo=timezone.utc)),
    ("7.36b", datetime(2024, 6, 6, 0, 0, tzinfo=timezone.utc)),
    ("7.37", datetime(2024, 11, 20, 0, 0, tzinfo=timezone.utc)),
    ("7.37b", datetime(2024, 12, 5, 0, 0, tzinfo=timezone.utc)),
]


def normalize_patch(raw: str | int | None) -> str:
    if raw is None:
        return "unknown"
    if isinstance(raw, int):
        s = str(raw)
    else:
        s = raw.strip().lower().lstrip("v")

    letter = ""
    if s and s[-1].isalpha():
        letter = s[-1]
        s = s[:-1]
    digits = [ch for ch in s if ch.isdigit()]
    if not digits:
        return "unknown"
    num = "".join(digits)
    if len(num) < 2:
        return "unknown"
    major = num[0]
    minor = num[1:3]
    rest = num[3:]
    base = f"{major}.{minor}"
    if letter:
        return f"{base}{letter}"
    if rest:
        return base
    return base


def infer_patch_from_time(start_time: datetime) -> str:
    if start_time.tzinfo is None:
        st = start_time.replace(tzinfo=timezone.utc)
    else:
        st = start_time.astimezone(timezone.utc)
    latest = "unknown"
    for tag, dt in _PATCH_DATES:
        if st >= dt:
            latest = tag
        else:
            break
    return latest


def current_patch() -> str:
    return os.getenv("CURRENT_PATCH", "unknown")


__all__ = ["normalize_patch", "infer_patch_from_time", "current_patch"]
