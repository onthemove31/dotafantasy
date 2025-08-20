from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime


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

    @app.get("/healthz", response_model=HealthResponse)
    async def healthz() -> HealthResponse:
        return HealthResponse(status="ok", timestamp=datetime.now(timezone.utc))

    return app


app = create_app()
