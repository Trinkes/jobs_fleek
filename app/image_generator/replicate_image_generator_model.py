import httpx
import replicate

from app.image_generator.image_generator_model import ImageGeneratorModel


class ReplicateImageGeneratorModel(ImageGeneratorModel):
    async def generate_image(self, prompt: str) -> httpx.SyncByteStream:
        outputs = await replicate.async_run(
            "black-forest-labs/flux-schnell",
            input={"prompt": "astronaut riding a rocket like a horse"},
        )
        return outputs
