import asyncio
import logging

import aioboto3
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration

from app.core.config import settings
from app.core.database import database_config
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


@celery_app.task
def create_media(media_id: MediaId):
    image_generator_model = DummyImageGeneratorModel(10)
    media_repository = MediaRepository(database_config.async_session_local)
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
    asyncio.run(image_generator.generate_image(media_id))
