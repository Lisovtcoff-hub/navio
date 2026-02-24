from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes.health import router as health_router

router = APIRouter()

# Public
router.include_router(health_router, tags=["health"])
