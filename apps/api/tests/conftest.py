"""
Pytest fixtures.

Tests run against a real PostgreSQL+PostGIS database, not SQLite. The schema
uses PostGIS geometry columns, JSONB and partial unique indexes, so a SQLite
stand-in would test a different schema than the one that ships - exactly the
kind of gap that lets a migration bug reach a live database.

Isolation strategy: the schema and seed data are created once per session and
committed for real; each test then runs inside an outer transaction with the
session joined via SAVEPOINT, so route handlers can call `db.commit()`
normally and everything is still rolled back when the test ends.
"""
from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.seed import run_seed

TEST_DB_SUFFIX = "_test"


def _test_database_url() -> URL:
    """
    Sibling database for tests, e.g. simhastha -> simhastha_test.

    Returns a URL object rather than a string on purpose: SQLAlchemy's
    ``str(URL)`` masks the password as ``***``, so round-tripping through a
    string here silently produces credentials that cannot authenticate.
    """
    url = make_url(settings.DATABASE_URL)
    return url.set(database=f"{url.database}{TEST_DB_SUFFIX}")


@pytest.fixture(scope="session")
def engine():
    """Create (or reuse) the test database, install PostGIS, build the schema."""
    admin_url = make_url(settings.DATABASE_URL)
    test_url = _test_database_url()

    # CREATE DATABASE cannot run inside a transaction block.
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": test_url.database},
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{test_url.database}"'))
    admin_engine.dispose()

    test_engine = create_engine(test_url, future=True)
    with test_engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        conn.commit()

    # Dropped first so a schema change between runs cannot leave a stale table
    # behind and produce a passing test against the wrong columns.
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)

    yield test_engine
    test_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def seeded(engine) -> None:
    """Load the real seed data once, committed, for the whole session."""
    with Session(engine) as session:
        run_seed(session)


@pytest.fixture()
def db(engine) -> Iterator[Session]:
    """A session whose writes are rolled back at the end of each test."""
    connection = engine.connect()
    transaction = connection.begin()
    # join_transaction_mode="create_savepoint" lets handler code call
    # db.commit() without ending the outer transaction we intend to roll back.
    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
    )
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db: Session) -> Iterator[TestClient]:
    """TestClient wired to the rolled-back session."""

    def _override_get_db() -> Iterator[Session]:
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# --------------------------------------------------------------------------
# Auth helpers
# --------------------------------------------------------------------------
def _login(client: TestClient, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login", json={"username": username, "password": password}
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture()
def super_admin_token(client: TestClient) -> str:
    return _login(
        client,
        settings.SEED_SUPER_ADMIN_USERNAME,
        settings.SEED_SUPER_ADMIN_PASSWORD,
    )


@pytest.fixture()
def content_manager_token(client: TestClient) -> str:
    return _login(
        client,
        settings.SEED_CONTENT_MANAGER_USERNAME,
        settings.SEED_CONTENT_MANAGER_PASSWORD,
    )


@pytest.fixture()
def public_user_token(client: TestClient) -> str:
    """A non-admin account - used to prove admin routes answer 403, not 200."""
    return _login(client, "pilgrim", "Pilgrim@2028")


@pytest.fixture()
def admin_headers(super_admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {super_admin_token}"}
