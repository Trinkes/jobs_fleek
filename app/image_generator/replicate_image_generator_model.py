from typing import AsyncIterator

import replicate
from replicate.exceptions import ModelError

from app.image_generator.image_generator_model import (
    ImageGeneratorModel,
    GenerateImageServiceError,
    GenericImageGeneratorError,
)


class ReplicateImageGeneratorModel(ImageGeneratorModel):
    # Note: This class may need adjustments as it hasn't been tested with the Replicate API.
    #
    # According to their documentation:
    # https://github.com/replicate/replicate-python?tab=readme-ov-file#run-a-model-and-stream-its-output
    #
    # It's possible to stream the response without loading the entire image file first,
    # which would be better for memory optimization. However, for simplicity, this implementation
    # loads the complete image and then "streams" it.

    async def generate_image(self, prompt: str) -> AsyncIterator[bytes]:
        try:
            file_output = await replicate.async_run(
                "black-forest-labs/flux-schnell",
                input={"prompt": prompt},
            )

            for chunk in file_output:
                yield chunk
        except ModelError as e:
            raise GenerateImageServiceError(str(e)) from e
        except BaseException as e:
            raise GenericImageGeneratorError(str(e)) from e
