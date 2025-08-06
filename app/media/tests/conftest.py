import pytest
from app.media.media_repository import MediaRepository
from tests.conftest import *  # noqa


@pytest.fixture(scope="session")
def media_repository(session) -> MediaRepository:
    return MediaRepository(session)
