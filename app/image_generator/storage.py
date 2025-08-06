import io
import uuid
from typing import AsyncIterator

import aioboto3
from pydantic import AnyUrl


class Storage:
    def __init__(self, aio_session: aioboto3.Session, bucket_name: str, s3_url: AnyUrl):
        self.s3_url = s3_url
        self.aio_session = aio_session
        self.bucket_name = bucket_name

    async def save_image(self, stream: AsyncIterator[bytes]) -> str:
        file_key = f"{uuid.uuid4()}.png"
        image_data = io.BytesIO()
        async for chunk in stream:
            image_data.write(chunk)
        image_data.seek(0)
        async with self.aio_session.resource(
            "s3",
            endpoint_url=self.s3_url,
        ) as s3:
            bucket = await s3.Bucket(self.bucket_name)
            await bucket.upload_fileobj(Fileobj=image_data, Key=file_key)
        return f"s3://{self.bucket_name}/{file_key}"
