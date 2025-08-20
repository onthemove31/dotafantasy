from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    opendota_base: str = os.getenv("OPENDOTA_BASE", "https://api.opendota.com/api")
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))


def get_settings() -> Settings:
    return Settings()
