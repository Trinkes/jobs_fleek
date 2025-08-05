import aioboto3
import pytest
from app.image_generator.dummy_image_generator.dummy_image_generator_model import (
    DummyImageGeneratorModel,
)
from app.image_generator.image_generator import ImageGenerator
from app.image_generator.storage import Storage
from app.media.media_repository import MediaRepository
from tests.conftest import *  # noqa
from app.media.tests.conftest import *  # noqa
from app.core.config import settings


@pytest.fixture(scope="session")
def image_generator(media_repository: MediaRepository) -> ImageGenerator:
    image_generator_model = DummyImageGeneratorModel()
    session = aioboto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION,
    )

    storage = Storage(
        aio_session=session,
        bucket_name=settings.BUCKET_NAME,
        s3_url=settings.S3_ENDPOINT_URL,
    )
    image_generator = ImageGenerator(
        image_generator_model, media_repository, storage=storage
    )
    return image_generator
