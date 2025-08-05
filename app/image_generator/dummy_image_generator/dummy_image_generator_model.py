import asyncio

import aiofiles
import httpx
from httpx import ByteStream

from app.core.config import settings
from app.image_generator.image_generator_model import ImageGeneratorModel


class DummyImageGeneratorModel(ImageGeneratorModel):
    def __init__(self, delay: int = 0):
        self.delay = delay

    async def generate_image(self, prompt: str) -> httpx.SyncByteStream:
        await asyncio.sleep(self.delay)
        async with aiofiles.open(
            settings.PROJECT_ROOT_DIR / "media" / "./dummy_image.png", "rb"
        ) as f:
            return ByteStream(await f.read())
