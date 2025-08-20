from .players import router as players_router
from .heroes import router as heroes_router
from .predict import router as predict_router
from .simulate import router as simulate_router

__all__ = [
    "players_router",
    "heroes_router",
    "predict_router",
    "simulate_router",
]
