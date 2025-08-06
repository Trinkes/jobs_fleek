import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from asyncpg.pgproto.pgproto import timedelta

from app.core.exceptions import ResourceNotFoundException
from app.image_generator.image_generator_model import (
    ImageGeneratorModel,
)
from app.image_generator.storage import Storage
from app.media.job_id import JobId
from app.media.media import Media
from app.media.media_id import MediaId
from app.media.media_repository import MediaRepository, MediaRepositoryDep
from app.media.media_status import MediaStatus

logger = logging.getLogger(__name__)


class TaskScheduler(ABC):
    @abstractmethod
    def schedule_media_generation(self, media_id: MediaId, eta: datetime) -> JobId:
        raise NotImplementedError


class ImageGenerator:
    def __init__(
        self,
        image_generator_model: ImageGeneratorModel,
        media_repository: MediaRepositoryDep,
        storage: Storage,
        task_scheduler: TaskScheduler,
        retry_delay_seconds_start: int = 1,
        max_retries: int = 5,
    ):
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

            return await self.media_repository.finish_media_generation(
                media.id, image_uri, MediaStatus.COMPLETED
            )
        except ResourceNotFoundException as error:
            logger.warning(f"no media found with {media_id} id.", exc_info=error)
        except Exception as error:
            logger.warning("image generation failed", exc_info=error)
            # we can, if needed, differentiate the exceptions based on ImageGeneratorModel#generate_image documentation
            # ex: if it's a GenerateImageServiceError and the service provide a time to wait, we could use it as next
            # try datetime

            # todo log error properly
            if media is not None:
                return await self.handle_failure(media)
            raise error

    async def handle_failure(self, media: Media):
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
        print(f"next_delay: {next_delay}")
        return datetime.now(tz=timezone.utc) + timedelta(seconds=next_delay)
