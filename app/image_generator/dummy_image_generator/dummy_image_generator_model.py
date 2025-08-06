import asyncio
import random
from typing import AsyncIterator

import aiofiles

from app.core.config import settings
from app.image_generator.image_generator_model import (
    ImageGeneratorModel,
    GenerateImageServiceError,
    GenericImageGeneratorError,
)


class DummyImageGeneratorModel(ImageGeneratorModel):
    def __init__(self, delay: int = 0, should_raise_error: bool = False):
        self.should_raise_errors = should_raise_error
        self.delay = delay

    async def generate_image(self, prompt: str) -> AsyncIterator[bytes]:
        await asyncio.sleep(self.delay)
        if self.should_raise_errors:
            if random.randint(1, 100) > 70:
                if random.randint(1, 100) > 80:
                    raise GenerateImageServiceError("test service error")
                else:
                    raise GenericImageGeneratorError("test generic error")

        async with aiofiles.open(
            settings.PROJECT_ROOT_DIR / "media" / "./dummy_image.png", "rb"
        ) as f:
            yield await f.read()
