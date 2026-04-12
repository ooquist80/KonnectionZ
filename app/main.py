from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.client import DatabaseClient


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    if not settings.skip_db_init:
        DatabaseClient(settings).initialize()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(production=settings.environment == "production")
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(api_router)
    origins = settings.allowed_origins
    # noinspection PyTypeChecker
    app.add_middleware(CORSMiddleware,
                       allow_origins=origins,
                       allow_credentials=True,
                       allow_methods=["*"],
                       allow_headers=["*"])
    return app


app = create_app()
