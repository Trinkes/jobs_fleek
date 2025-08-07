import pytest

from app.logs.log_crud import LogsRepository
from tests.conftest import *  # noqa


@pytest.fixture(scope="session")
def logs_repository(session) -> LogsRepository:
    return LogsRepository(session)
