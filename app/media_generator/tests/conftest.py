import uuid
from datetime import datetime

import aioboto3
import pytest

from app.media_generator.dummy_media_generator.dummy_media_generator_model import (
    ErrorSimulator,
    DummyMediaGeneratorModel,
)
from app.media_generator.media_generator import MediaGenerator
from app.media_generator.task_scheduler import TaskScheduler
from app.media_generator.storage import Storage
from app.logs.log_crud import LogsRepository
from app.media.job_id import JobId
from app.media.media_id import MediaId
from app.media.media_repository import MediaRepository
from tests.conftest import *  # noqa
from app.media.tests.conftest import *  # noqa
from app.logs.tests.conftest import *  # noqa
from app.core.config import settings


@pytest.fixture(scope="session")
def task_scheduler() -> TaskScheduler:
    class DummyTaskScheduler(TaskScheduler):
        def schedule_media_generation(self, media_id: MediaId, eta: datetime) -> JobId:
            return uuid.uuid4()

    return DummyTaskScheduler()


@pytest.fixture(scope="session")
def storage():
    session = aioboto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION,
    )

    return Storage(
        aio_session=session,
        bucket_name=settings.BUCKET_NAME,
        s3_url=settings.S3_ENDPOINT_URL,
    )


@pytest.fixture(scope="session")
def media_generator(
    media_repository: MediaRepository,
    task_scheduler,
    logs_repository: LogsRepository,
    storage: Storage,
) -> MediaGenerator:
    class NoErrorErrorSimulator(ErrorSimulator):
        def maybe_raise_error(self):
            pass

    media_generator_model = DummyMediaGeneratorModel(NoErrorErrorSimulator())

    media_generator = MediaGenerator(
        media_generator_model,
        media_repository,
        storage=storage,
        task_scheduler=task_scheduler,
        logs_repository=logs_repository,
    )
    return media_generator
