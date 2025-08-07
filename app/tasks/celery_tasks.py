import contextlib
import logging
import random
from datetime import datetime
from typing import AsyncGenerator

import aioboto3
import sentry_sdk
from asgiref.sync import async_to_sync
from sentry_sdk.integrations.celery import CeleryIntegration
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.media_generator.dummy_media_generator.dummy_media_generator_model import (
    ErrorSimulator,
    DummyMediaGeneratorModel,
)
from app.media_generator.media_generator import MediaGenerator
from app.media_generator.media_generator_model import (
    GenericMediaGeneratorError,
    GenerateMediaServiceError,
)
from app.media_generator.task_scheduler import TaskScheduler
from app.media_generator.storage import Storage
from app.logs.log_crud import LogsRepository
from app.media.job_id import JobId
from app.media.media_id import MediaId
from app.media.media_repository import MediaRepository
from app.tasks.celery import celery_app

logger = logging.getLogger(__name__)

if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(
        dsn=str(settings.SENTRY_DSN),
        enable_tracing=True,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        integrations=[
            CeleryIntegration(
                monitor_beat_tasks=True,
            ),
        ],
    )


@celery_app.task
def celery_health_check(*, message: str):
    return {"statusCode": 200, "message": message}


@contextlib.asynccontextmanager
async def get_db_session_maker() -> AsyncGenerator:
    async_engine = create_async_engine(f"{settings.ASYNC_SQLALCHEMY_DATABASE_URI}")
    try:
        db = async_sessionmaker(
            async_engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
        yield db
    finally:
        await async_engine.dispose()


async def _generate_media(media_id: MediaId):
    class ServiceErrorSimulator(ErrorSimulator):
        def maybe_raise_error(self):
            if random.randint(1, 100) > 70:
                if random.randint(1, 100) > 80:
                    raise GenerateMediaServiceError("test service error")
                else:
                    raise GenericMediaGeneratorError("test generic error")

    media_generator_model = DummyMediaGeneratorModel(ServiceErrorSimulator(), 5)
    async with get_db_session_maker() as db_session:
        media_repository = MediaRepository(db_session)
        session = aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION,
        )

        storage = Storage(
            aio_session=session,
            bucket_name=settings.BUCKET_NAME,
            s3_url=settings.S3_ENDPOINT_URL,
        )

        class CeleryTaskScheduler(TaskScheduler):
            def schedule_media_generation(
                self, media_id: MediaId, eta: datetime
            ) -> JobId:
                return create_media.apply_async(
                    kwargs={"media_id": str(media_id)}, eta=eta
                ).id

        log_repository = LogsRepository(db_session)
        media_generator = MediaGenerator(
            media_generator_model,
            media_repository,
            storage=storage,
            task_scheduler=CeleryTaskScheduler(),
            logs_repository=log_repository,
        )
        media = await media_generator.generate_media(media_id)
        if media is None:
            return None
        else:
            return media.model_dump_json()


@celery_app.task(bind=True)
def create_media(self, media_id: MediaId):
    try:
        return async_to_sync(_generate_media)(media_id)
    except Exception as error:
        logging.error(f"task: {self.request.id} error", exc_info=error)
