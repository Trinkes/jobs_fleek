import pytest

from app.core.exceptions import ResourceNotFoundException
from app.image_generator.dummy_image_generator.dummy_image_generator_model import (
    DummyImageGeneratorModel,
    ErrorSimulator,
)
from app.image_generator.image_generator import ImageGenerator
from app.image_generator.image_generator_model import (
    GenerateImageServiceError,
)
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


class NoErrorErrorSimulator(ErrorSimulator):
    next_exception_to_raise: Exception | None = None

    def maybe_raise_error(self):
        exception = self.next_exception_to_raise
        self.next_exception_to_raise = None
        raise exception


@pytest.mark.asyncio
async def test_generate_image_error(
    media_repository: MediaRepository,
    logs_repository,
    storage,
    task_scheduler,
):
    simulator = NoErrorErrorSimulator()
    image_generator = ImageGenerator(
        DummyImageGeneratorModel(simulator, 0),
        media_repository,
        logs_repository,
        storage,
        task_scheduler,
    )

    simulator.next_exception_to_raise = GenerateImageServiceError("test Service error")
    media = await media_repository.create_media(prompt="this is a test prompt")
    media = await image_generator.generate_image(media.id)
    assert media.status is MediaStatus.IN_QUEUE

    simulator.next_exception_to_raise = ResourceNotFoundException("test generic error")
    media = await media_repository.create_media(prompt="this is a test prompt")
    media = await image_generator.generate_image(media.id)
    assert media is None
