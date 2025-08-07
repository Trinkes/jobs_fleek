import pytest

from app.core.exceptions import ResourceNotFoundException
from app.media.media_repository import MediaRepository
from app.media.media_status import MediaStatus
from app.media_generator.dummy_media_generator.dummy_media_generator_model import (
    ErrorSimulator,
    DummyMediaGeneratorModel,
)
from app.media_generator.media_generator import MediaGenerator
from app.media_generator.media_generator_model import GenerateMediaServiceError


@pytest.mark.asyncio
async def test_generate_media(
    media_generator: MediaGenerator, media_repository: MediaRepository
):
    media = await media_repository.create_media(prompt="this is a test prompt")
    generated_media = await media_generator.generate_media(media.id)
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
async def test_generate_media_error(
    media_repository: MediaRepository,
    logs_repository,
    storage,
    task_scheduler,
):
    simulator = NoErrorErrorSimulator()
    media_generator = MediaGenerator(
        DummyMediaGeneratorModel(simulator, 0),
        media_repository,
        logs_repository,
        storage,
        task_scheduler,
    )

    simulator.next_exception_to_raise = GenerateMediaServiceError("test Service error")
    media = await media_repository.create_media(prompt="this is a test prompt")
    media = await media_generator.generate_media(media.id)
    assert media.status is MediaStatus.IN_QUEUE

    simulator.next_exception_to_raise = ResourceNotFoundException("test generic error")
    media = await media_repository.create_media(prompt="this is a test prompt")
    media = await media_generator.generate_media(media.id)
    assert media is None
