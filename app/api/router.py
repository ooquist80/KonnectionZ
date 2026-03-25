from fastapi import APIRouter

from app.api.endpoints.health import router as health_router
from app.api.endpoints.wordsets import router as wordsets_router
from app.api.endpoints.gamesets import router as gamesets_router
from app.api.endpoints.games import router as games_router
from app.api.endpoints.users import router as users_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(wordsets_router)
api_router.include_router(gamesets_router)
api_router.include_router(users_router)
api_router.include_router(games_router)
