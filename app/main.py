from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.db.client import DatabaseClient


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    if not settings.skip_db_init:
        DatabaseClient(settings).initialize()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(api_router)
    return app


app = create_app()

