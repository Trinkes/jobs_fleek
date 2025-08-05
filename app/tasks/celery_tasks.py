import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration

from app.core.config import settings
from app.media.media_id import MediaId
from app.tasks.celery import celery_app
import logging

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
    pass
