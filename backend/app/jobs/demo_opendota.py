import asyncio
from app.clients.opendota import OpenDotaClient


async def main():
    async with OpenDotaClient() as od:
        pros = await od.get_pro_players()
        pro = next((p for p in pros if p.account_id), None)
        if not pro:
            print("No pro players found")
            return
        matches = await od.get_player_matches(pro.account_id, limit=25)
        hydrated = []
        for m in matches[:15]:
            d = await od.get_match_details(m.match_id)
            hydrated.append(d.match_id)
        print("Hydrated match ids:", hydrated[:10])


if __name__ == "__main__":
    asyncio.run(main())
