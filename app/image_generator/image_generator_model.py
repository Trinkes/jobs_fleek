import abc
from abc import ABC

import httpx
from httpx import ByteStream


class ImageGeneratorModel(ABC):
    @abc.abstractmethod
    async def generate_image(self, prompt: str) -> httpx.SyncByteStream | ByteStream:
        pass
