import pytest
from starlette.testclient import TestClient

from app.main import fastapi_app


@pytest.fixture(scope="session")
def test_client():
    return TestClient(fastapi_app)
