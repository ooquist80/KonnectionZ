from fastapi import APIRouter

from app.api.endpoints.health import router as health_router
from app.api.endpoints.wordsets import router as wordsets_router
from app.api.endpoints.games import router as games_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(wordsets_router)
api_router.include_router(games_router)
