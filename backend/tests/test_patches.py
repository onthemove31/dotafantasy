from __future__ import annotations

from datetime import datetime, timezone

from app.utils.patches import normalize_patch, infer_patch_from_time


def test_normalize_patch_cases():
    assert normalize_patch("7.37b") == "7.37b"
    assert normalize_patch("v7.37b") == "7.37b"
    assert normalize_patch("7.37") == "7.37"
    assert normalize_patch(737) == "7.37"
    assert normalize_patch("foo") == "unknown"


def test_infer_patch():
    dt = datetime(2024, 12, 6, tzinfo=timezone.utc)
    assert infer_patch_from_time(dt) in ("7.37", "7.37b")
