import abc
from abc import ABC
from typing import AsyncIterator


class GenerateMediaServiceError(Exception):
    pass


class GenericMediaGeneratorError(Exception):
    pass


class MediaGeneratorModel(ABC):
    @abc.abstractmethod
    async def generate_media(self, prompt: str) -> AsyncIterator[bytes]:
        """
        Generate an media file based on the provided prompt.

        Args:
            prompt: The text prompt to generate an image from

        Returns:
            AsyncIterator[bytes]: The generated media as a byte stream iterator

        Raises:
            GenerateMediaServiceError: If there's a problem related to the media generator service
            GenericMediaGeneratorError: For any other errors that occur during media generation
        """
        # using the folloing to avoid the following warning when using this interface:
        # Expected type 'AsyncIterator[bytes]', got 'Coroutine[Any, Any, AsyncIterator[bytes]]' instead

        if False:
            yield b""
