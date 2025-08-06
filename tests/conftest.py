import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.main import fastapi_app


@pytest.fixture(scope="session")
def session():
    test_engine = create_async_engine(
        str(settings.SQLALCHEMY_DATABASE_URI),
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
    return test_session_maker


@pytest.fixture(scope="session")
def test_client():
    with TestClient(fastapi_app) as client:
        yield client
