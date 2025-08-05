import io

from app.image_generator.image_generator_model import ImageGeneratorModel
from app.image_generator.storage import Storage
from app.media.media import Media
from app.media.media_id import MediaId
from app.media.media_repository import MediaRepository, MediaRepositoryDep
from app.media.media_status import MediaStatus


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

    async def generate_image(self, media_id: MediaId) -> Media:
        media = await self.media_repository.get_and_update_status(
            media_id, MediaStatus.IN_QUEUE, MediaStatus.PROCESSING
        )
        image_bytes = await self.image_generator_model.generate_image(media.prompt)
        data = b"".join(image_bytes)
        image_uri = await self.storage.save_image(io.BytesIO(data))
        return await self.media_repository.update_media_uri(
            media.id, image_uri, MediaStatus.COMPLETED
        )
