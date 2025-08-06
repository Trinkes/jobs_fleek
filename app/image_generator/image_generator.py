import logging
from datetime import datetime, timezone

from asyncpg.pgproto.pgproto import timedelta

from app.core.exceptions import ResourceNotFoundException
from app.image_generator.image_generator_model import (
    ImageGeneratorModel,
)
from app.image_generator.storage import Storage
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
        storage: Storage,
    ):
        self.storage = storage
        self.media_repository: MediaRepository = media_repository
        self.image_generator_model = image_generator_model

    async def generate_image(self, media_id: MediaId) -> Media | None:
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

            # todo exponential backoff
            # todo log error
            return await self.media_repository.register_media_generation_error(
                media_id, datetime.now(tz=timezone.utc) + timedelta(seconds=2)
            )
