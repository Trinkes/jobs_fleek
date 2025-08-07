import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

import aiofiles

from app.core.config import settings
from app.image_generator.image_generator_model import (
    ImageGeneratorModel,
)


class ErrorSimulator(ABC):
    @abstractmethod
    def maybe_raise_error(self):
        """
        this interface should be used to simulate errors
        :return:
        """
        raise NotImplementedError()


class DummyImageGeneratorModel(ImageGeneratorModel):
    def __init__(
        self,
        error_simulator: ErrorSimulator,
        delay: int = 0,
    ):
        self.error_simulator = error_simulator
        self.delay = delay

    async def generate_image(self, prompt: str) -> AsyncIterator[bytes]:
        await asyncio.sleep(self.delay)
        self.error_simulator.maybe_raise_error()

        async with aiofiles.open(
            settings.PROJECT_ROOT_DIR / "media" / "./dummy_image.png", "rb"
        ) as f:
            yield await f.read()
