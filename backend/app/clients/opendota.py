from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field
try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
    )
except Exception:  # pragma: no cover - fallback for local envs without tenacity
    def retry(*_args, **_kwargs):  # type: ignore[misc]
        def _wrap(fn):
            return fn

        return _wrap

    def stop_after_attempt(*_args, **_kwargs):  # type: ignore[misc]
        return None

    def wait_exponential(*_args, **_kwargs):  # type: ignore[misc]
        return None

    def retry_if_exception_type(*_args, **_kwargs):  # type: ignore[misc]
        return None

from app.config.env import get_settings


class ProPlayer(BaseModel):
    account_id: int
    personaname: Optional[str] = None
    name: Optional[str] = None
    team_name: Optional[str] = None


class PlayerMatch(BaseModel):
    match_id: int
    start_time: Optional[int] = None


class MatchDetails(BaseModel):
    match_id: int
    start_time: int
    duration: int
    patch: Optional[str] = Field(default=None)
    radiant_win: bool


@dataclass
class _RateLimiter:
    capacity: int
    window: int
    tokens: int
    reset_at: float

    @classmethod
    def create(cls, capacity: int, window: int) -> "_RateLimiter":
        now = time.monotonic()
        return cls(capacity=capacity, window=window, tokens=capacity, reset_at=now + window)

    async def acquire(self) -> None:
        while True:
            now = time.monotonic()
            if now >= self.reset_at:
                self.tokens = self.capacity
                self.reset_at = now + self.window
            if self.tokens > 0:
                self.tokens -= 1
                return
            # sleep until window resets
            await asyncio.sleep(max(0.0, self.reset_at - now))


class OpenDotaClient:
    def __init__(self, base_url: Optional[str] = None, client: Optional[httpx.AsyncClient] = None):
        settings = get_settings()
        self.base_url = base_url or settings.opendota_base
        self._client = client or httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        self._limiter = _RateLimiter.create(settings.rate_limit_requests, settings.rate_limit_window)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "OpenDotaClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        await self.aclose()

    @retry(
        reraise=True,
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
        stop=stop_after_attempt(5),
    )
    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        await self._limiter.acquire()
        resp = await self._client.get(path, params=params)
        if resp.status_code == 429:
            # raise to trigger retry/backoff
            resp.raise_for_status()
        resp.raise_for_status()
        return resp.json()

    async def get_pro_players(self) -> List[ProPlayer]:
        data = await self._get("/proPlayers")
        return [ProPlayer(**item) for item in data]

    async def get_player_matches(self, account_id: int, limit: int = 50) -> List[PlayerMatch]:
        data = await self._get(f"/players/{account_id}/matches", params={"limit": limit})
        return [PlayerMatch(**item) for item in data]

    async def get_match_details(self, match_id: int) -> MatchDetails:
        data = await self._get(f"/matches/{match_id}")
        return MatchDetails(**data)
