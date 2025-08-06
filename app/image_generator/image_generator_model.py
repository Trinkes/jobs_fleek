import abc
from abc import ABC
from typing import AsyncIterator


class GenerateImageServiceError(BaseException):
    pass


class GenericImageGeneratorError(BaseException):
    pass


class ImageGeneratorModel(ABC):
    @abc.abstractmethod
    async def generate_image(self, prompt: str) -> AsyncIterator[bytes]:
        """
        Generate an image based on the provided prompt.

        Args:
            prompt: The text prompt to generate an image from

        Returns:
            AsyncIterator[bytes]: The generated image as a byte stream iterator

        Raises:
            GenerateImageServiceError: If there's a problem related to the image generator service
            GenericImageGeneratorError: For any other errors that occur during image generation
        """
        # using the folloing to avoid the following warning when using this interface:
        # Expected type 'AsyncIterator[bytes]', got 'Coroutine[Any, Any, AsyncIterator[bytes]]' instead

        if False:
            yield b""
