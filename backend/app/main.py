from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


def create_app() -> FastAPI:
    app = FastAPI(title="dota-fantasy API", version="0.1.0")

    # CORS for local dev (vite on 5173)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    # Routers
    from app.routers import players_router, heroes_router, predict_router, simulate_router
    app.include_router(players_router)
    app.include_router(heroes_router)
    app.include_router(predict_router)
    app.include_router(simulate_router)

    return app


app = create_app()
