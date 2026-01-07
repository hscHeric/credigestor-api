from __future__ import annotations

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.database as app_database
import app.main as app_main

# Base no seu projeto está em app.database
Base = app_database.Base


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture(scope="session", autouse=True)
def patch_app_engine(test_engine):
    """
    Garante que:
    - app.database.engine usa SQLite
    - app.main.engine usa SQLite
    - Base.metadata.create_all cria tabelas no SQLite (não no Postgres)
    """
    app_database.engine = test_engine
    app_main.engine = test_engine

    import app.models  # noqa: F401

    Base.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture()
def db_session(test_engine):
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    app_database.SessionLocal = TestingSessionLocal

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app_main.app.dependency_overrides[app_database.get_db] = override_get_db
    with TestClient(app_main.app) as c:
        yield c
    app_main.app.dependency_overrides.clear()
