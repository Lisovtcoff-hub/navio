from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging(debug=settings.debug)

    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        debug=settings.debug,
    )

    # CORS (tighten for prod; in local we allow localhost origins)
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )

    # Routers
    app.include_router(v1_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
