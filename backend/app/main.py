from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging(settings.LOG_LEVEL)
    app = FastAPI(title="Navio API", version="0.1.0")
    app.include_router(v1_router, prefix="/api/v1")
    return app


app = create_app()
