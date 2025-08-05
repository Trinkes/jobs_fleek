import pytest
from app.media.media_repository import MediaRepository
from tests.conftest import *  # noqa
from app.core.database import database_config


@pytest.fixture(scope="session")
def media_repository() -> MediaRepository:
    return MediaRepository(database_config.async_session_local)
