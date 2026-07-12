"""Shared pytest fixtures.

Tests run against a real (throwaway) Postgres database so the timezone-aware
datetimes and the UNIQUE(service_id, slot_start) double-booking guard behave
exactly as they do in production. The database is created if it doesn't exist,
and every test gets a freshly built schema (create_all / drop_all).

Point at a different DB by setting TEST_DATABASE_URL, e.g. in CI.
"""
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

# Importing the app pulls in every router -> every model, so Base.metadata
# knows about all tables before we call create_all().
from app.main import app
from app.database import Base
from app.deps import get_db

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/appointments_test",
)


def _ensure_database(url_str: str) -> None:
    """Create the test database if it isn't there yet (connect to `postgres` to do it)."""
    url = make_url(url_str)
    admin_engine = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": url.database},
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    admin_engine.dispose()


_ensure_database(TEST_DATABASE_URL)

engine = create_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def _schema():
    """Fresh schema around every test — full isolation, no cross-test state."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """A TestClient whose get_db points at the test database."""
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def login_as(client):
    """Register + log in a user, returning ready-to-use Authorization headers."""
    def _login(email: str, password: str = "password123") -> dict:
        client.post("/auth/register", json={"email": email, "password": password})
        res = client.post("/auth/login", json={"email": email, "password": password})
        assert res.status_code == 200, res.text
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    return _login
