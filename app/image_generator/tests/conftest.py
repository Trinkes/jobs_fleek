import uuid
from datetime import datetime

import aioboto3
import pytest
from app.image_generator.dummy_image_generator.dummy_image_generator_model import (
    DummyImageGeneratorModel,
    ErrorSimulator,
)
from app.image_generator.image_generator import ImageGenerator, TaskScheduler
from app.image_generator.storage import Storage
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
def image_generator(
    media_repository: MediaRepository,
    task_scheduler,
    logs_repository: LogsRepository,
    storage: Storage,
) -> ImageGenerator:
    class NoErrorErrorSimulator(ErrorSimulator):
        def maybe_raise_error(self):
            pass

    image_generator_model = DummyImageGeneratorModel(NoErrorErrorSimulator())

    image_generator = ImageGenerator(
        image_generator_model,
        media_repository,
        storage=storage,
        task_scheduler=task_scheduler,
        logs_repository=logs_repository,
    )
    return image_generator
