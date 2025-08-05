import pytest

from app.image_generator.image_generator import ImageGenerator
from app.media.media_repository import MediaRepository
from app.media.media_status import MediaStatus


@pytest.mark.asyncio
async def test_generate_image(
    image_generator: ImageGenerator, media_repository: MediaRepository
):
    media = await media_repository.create_media(prompt="this is a test prompt")
    generated_media = await image_generator.generate_image(media.id)
    assert media.id == generated_media.id
    assert generated_media.status is MediaStatus.COMPLETED
    assert generated_media.media_uri is not None
