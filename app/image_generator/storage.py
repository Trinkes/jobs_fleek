import uuid
from typing import BinaryIO

import aioboto3
from pydantic import AnyUrl


class Storage:
    def __init__(self, aio_session: aioboto3.Session, bucket_name: str, s3_url: AnyUrl):
        self.s3_url = s3_url
        self.aio_session = aio_session
        self.bucket_name = bucket_name

    async def save_image(self, stream: BinaryIO) -> str:
        file_key = f"{uuid.uuid4()}.png"
        async with self.aio_session.resource(
            "s3",
            endpoint_url=self.s3_url,
        ) as s3:
            bucket = await s3.Bucket(self.bucket_name)
            await bucket.upload_fileobj(Fileobj=stream, Key=file_key)
        return f"s3://{self.bucket_name}/{file_key}"
