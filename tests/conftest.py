import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.database import database_config
from app.main import fastapi_app


@pytest.fixture(scope="session", autouse=True)
def setup_test_async_engine():
    """Configure async engine for tests that works with TestClient."""
    # Use psycopg instead of asyncpg for tests to avoid event loop issues
    # Convert asyncpg URL to psycopg URL
    test_url = str(settings.ASYNC_SQLALCHEMY_DATABASE_URI).replace(
        "postgresql+asyncpg://", "postgresql+psycopg://"
    )

    test_engine = create_async_engine(
        test_url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    test_session_maker = async_sessionmaker(
        test_engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    # Override the database config
    original_engine = database_config.async_engine
    original_session_maker = database_config.async_session_local

    database_config.async_engine = test_engine
    database_config.async_session_local = test_session_maker

    yield

    # Restore original config
    database_config.async_engine = original_engine
    database_config.async_session_local = original_session_maker


@pytest.fixture(scope="session")
def test_client():
    return TestClient(fastapi_app)
