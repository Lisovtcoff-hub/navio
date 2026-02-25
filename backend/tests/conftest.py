import os
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.main import create_app
from app.models import Base


@pytest.fixture(scope="session")
def engine():
    # Для простоты используем тот же DATABASE_URL, что в .env / docker.
    # В будущем можно сделать отдельную тестовую БД.
    url = os.getenv("DATABASE_URL")
    if not url:
        # fallback: собрать из env POSTGRES_*
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "navio")
        user = os.getenv("POSTGRES_USER", "navio")
        password = os.getenv("POSTGRES_PASSWORD", "navio")
        url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"

    eng = create_engine(url, pool_pre_ping=True)
    Base.metadata.create_all(bind=eng)
    return eng


@pytest.fixture()
def db(engine) -> Generator[Session, None, None]:
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    app = create_app()
    from fastapi.testclient import TestClient

    return TestClient(app)
