import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.deps import get_db

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health")
def health():
    logger.debug("Health endpoint called")
    return {"status": "ok"}


@router.get("/health/db")
def health_db(db: Annotated[Session, Depends(get_db)]):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "okok"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "error", "details": str(e)}
