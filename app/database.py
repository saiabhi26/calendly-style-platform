from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,   # check a pooled connection is alive before use (serverless DBs drop idle ones)
    pool_recycle=300,     # proactively recycle connections older than 5 min
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass