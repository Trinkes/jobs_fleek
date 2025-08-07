import logging
import traceback
from datetime import datetime, timezone, timedelta

from app.core.exceptions import ResourceNotFoundException
from app.image_generator.image_generator_model import (
    ImageGeneratorModel,
)
from app.image_generator.storage import Storage
from app.image_generator.task_scheduler import TaskScheduler
from app.logs.log_crud import LogRepositoryDep
from app.logs.log_level import LogLevel
from app.media.media import Media
from app.media.media_id import MediaId
from app.media.media_repository import MediaRepository, MediaRepositoryDep
from app.media.media_status import MediaStatus

logger = logging.getLogger(__name__)


class ImageGenerator:
    def __init__(
        self,
        image_generator_model: ImageGeneratorModel,
        media_repository: MediaRepositoryDep,
        logs_repository: LogRepositoryDep,
        storage: Storage,
        task_scheduler: TaskScheduler,
        retry_delay_seconds_start: int = 1,
        max_retries: int = 5,
    ):
        self.logs_repository = logs_repository
        self.max_retries = max_retries
        self.retry_delay_seconds_start = retry_delay_seconds_start
        self.task_scheduler = task_scheduler
        self.storage = storage
        self.media_repository: MediaRepository = media_repository
        self.image_generator_model = image_generator_model

    async def generate_image(self, media_id: MediaId) -> Media | None:
        media = None
        try:
            media = await self.media_repository.get_and_update_status(
                media_id, MediaStatus.IN_QUEUE, MediaStatus.PROCESSING
            )
            image_bytes_iter = self.image_generator_model.generate_image(media.prompt)
            image_uri = await self.storage.save_image(image_bytes_iter)

            media = await self.media_repository.finish_media_generation(
                media.id, image_uri, MediaStatus.COMPLETED
            )
            await self.log_run(media)
            return media
        except ResourceNotFoundException as error:
            logger.warning(f"no media found with {media_id} id.", exc_info=error)
            await self.log_error(error)
            return None
        except Exception as error:
            logger.warning("image generation failed", exc_info=error)
            # we can, if needed, differentiate the exceptions based on ImageGeneratorModel#generate_image documentation
            # ex: if it's a GenerateImageServiceError and the service provide a time to wait, we could use it as next
            # try datetime

            await self.log_error(error, media)
            if media is not None:
                return await self.handle_failure(media)
            raise error

    async def log_error(self, error: Exception, media: Media | None = None):
        obj_type = type(error)
        exception_type = f"{obj_type.__module__}.{obj_type.__qualname__}"
        extras = {
            "exception_type": exception_type,
            "stack_trace": "".join(
                traceback.format_exception(type(error), error, error.__traceback__)
            ),
        }
        if media is not None:
            extras["media_id"] = str(media.id)
            extras = media.model_dump() | extras

        await self.logs_repository.log(
            "ImageGenerator",
            LogLevel.ERROR,
            "Image generation failed",
            extras,
        )

    async def handle_failure(self, media: Media) -> Media:
        if media.number_of_tries < self.max_retries:
            next_try = await self.calculate_next_try(media)
            job_id = self.task_scheduler.schedule_media_generation(media.id, next_try)
            return await self.media_repository.register_media_generation_error(
                media.id, next_try, job_id, MediaStatus.IN_QUEUE
            )
        else:
            return await self.media_repository.register_media_generation_error(
                media.id, None, None, MediaStatus.ERROR
            )

    async def calculate_next_try(self, media: Media) -> datetime:
        next_delay = self.retry_delay_seconds_start * (2**media.number_of_tries)
        return datetime.now(tz=timezone.utc) + timedelta(seconds=next_delay)

    async def log_run(self, media: Media):
        await self.logs_repository.log(
            "ImageGenerator",
            LogLevel.INFO,
            "Image generation completed",
            media.model_dump(),
        )
