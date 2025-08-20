from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "media_processing",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
    beat_schedule_filename=None,  # Disable the default SQLite schedule
    timezone="UTC",
)

celery_app.autodiscover_tasks(["app.tasks.celery_tasks"], force=True)
