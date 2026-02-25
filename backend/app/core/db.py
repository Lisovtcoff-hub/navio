import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def build_database_url() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "navio")
    user = os.getenv("POSTGRES_USER", "navio")
    password = os.getenv("POSTGRES_PASSWORD", "navio")

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


DATABASE_URL = build_database_url()

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
