from typing import AsyncIterator

import replicate
from replicate.exceptions import ModelError

from app.media_generator.media_generator_model import (
    MediaGeneratorModel,
    GenerateMediaServiceError,
    GenericMediaGeneratorError,
)


class ReplicateMediaGeneratorModel(MediaGeneratorModel):
    # Note: This class may need adjustments as it hasn't been tested with the Replicate API.
    #
    # According to their documentation:
    # https://github.com/replicate/replicate-python?tab=readme-ov-file#run-a-model-and-stream-its-output
    #
    # It's possible to stream the response without loading the entire image file first,
    # which would be better for memory optimization. However, for simplicity, this implementation
    # loads the complete image and then "streams" it.

    async def generate_media(self, prompt: str) -> AsyncIterator[bytes]:
        try:
            file_output = await replicate.async_run(
                "black-forest-labs/flux-schnell",
                input={"prompt": prompt},
            )

            for chunk in file_output:
                yield chunk
        except ModelError as e:
            raise GenerateMediaServiceError(str(e)) from e
        except BaseException as e:
            raise GenericMediaGeneratorError(str(e)) from e
