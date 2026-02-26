import os

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.deps.db import get_db
from app.main import create_app
from app.models import Base


@pytest.fixture(scope="session")
def engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "navio")
        user = os.getenv("POSTGRES_USER", "navio")
        password = os.getenv("POSTGRES_PASSWORD", "navio")
        url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"

    eng = create_engine(url, pool_pre_ping=True)

    # Один раз на сессию тестов: создаём все таблицы
    Base.metadata.create_all(bind=eng)
    return eng


@pytest.fixture()
def db(engine):
    connection = engine.connect()
    connection.begin()  # <-- не сохраняем outer transaction object

    TestingSessionLocal = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session: Session = TestingSessionLocal()

    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    try:
        yield session
    finally:
        session.close()
        # откатываем через connection, а не через outer-объект
        connection.rollback()
        connection.close()


@pytest.fixture()
def client(db):
    """
    Подменяем dependency get_db так, чтобы ручки FastAPI использовали
    ТОТ ЖЕ session, что и тест.
    """
    app = create_app()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    from fastapi.testclient import TestClient

    return TestClient(app)
