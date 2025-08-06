import contextlib
import logging
from typing import AsyncGenerator

import aioboto3
import sentry_sdk
from asgiref.sync import async_to_sync
from sentry_sdk.integrations.celery import CeleryIntegration
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.image_generator.dummy_image_generator.dummy_image_generator_model import (
    DummyImageGeneratorModel,
)
from app.image_generator.image_generator import ImageGenerator
from app.image_generator.storage import Storage
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
    image_generator_model = DummyImageGeneratorModel(0, False)
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
        image_generator = ImageGenerator(
            image_generator_model, media_repository, storage=storage
        )
        media = await image_generator.generate_image(media_id)
        if media is None:
            return None
        else:
            return media.model_dump_json()


@celery_app.task(bind=True)
def create_media(self, media_id: MediaId):
    try:
        return async_to_sync(_generate_media)(media_id)
    except BaseException as error:
        logging.error(f"task: {self.request.id} error", exc_info=error)
