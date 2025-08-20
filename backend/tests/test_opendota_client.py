import asyncio
from typing import Any

import httpx
import pytest

from app.clients.opendota import OpenDotaClient, ProPlayer, PlayerMatch, MatchDetails


class MockTransport(httpx.AsyncBaseTransport):
    def __init__(self, routes: dict[str, Any]):
        self.routes = routes

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:  # type: ignore[override]
        key = (request.method, request.url.path, tuple(sorted(request.url.params.multi_items())))
        if key in self.routes:
            status, json_data = self.routes[key]
            return httpx.Response(status, json=json_data)
        return httpx.Response(404, json={"detail": "not found"})


@pytest.mark.asyncio
async def test_get_pro_players_and_matches_and_match_details():
    routes = {
        ("GET", "/proPlayers", ()): (200, [{"account_id": 1, "personaname": "pro1"}]),
        ("GET", "/players/1/matches", (("limit", "2"),)): (
            200,
            [{"match_id": 100}, {"match_id": 101}],
        ),
        ("GET", "/matches/100", ()): (
            200,
            {"match_id": 100, "start_time": 1, "duration": 3000, "patch": "7.37b", "radiant_win": True},
        ),
    }
    transport = MockTransport(routes)
    async with httpx.AsyncClient(base_url="https://api.opendota.com/api", transport=transport) as client:
        od = OpenDotaClient(client=client)
        players = await od.get_pro_players()
        assert [p.account_id for p in players] == [1]

        matches = await od.get_player_matches(1, limit=2)
        assert [m.match_id for m in matches] == [100, 101]

        details = await od.get_match_details(100)
        assert isinstance(details, MatchDetails)
        assert details.match_id == 100

        await od.aclose()
