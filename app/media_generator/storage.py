import io
import uuid
from typing import AsyncIterator, Annotated

import aioboto3
from fastapi import Depends
from pydantic import AnyUrl

from app.core.config import settings


class Storage:
    def __init__(self, aio_session: aioboto3.Session, bucket_name: str, s3_url: AnyUrl):
        self.s3_url = s3_url
        self.aio_session = aio_session
        self.bucket_name = bucket_name

    async def save_bytes(self, stream: AsyncIterator[bytes]) -> str:
        file_key = f"{uuid.uuid4()}.png"
        bytes_data = io.BytesIO()
        async for chunk in stream:
            bytes_data.write(chunk)
        bytes_data.seek(0)
        async with self.aio_session.resource(
            "s3",
            endpoint_url=self.s3_url,
        ) as s3:
            bucket = await s3.Bucket(self.bucket_name)
            await bucket.upload_fileobj(Fileobj=bytes_data, Key=file_key)
        return f"s3://{self.bucket_name}/{file_key}"

    async def create_media_url(self, uri: str) -> AnyUrl:
        if not uri.startswith("s3://"):
            raise ValueError("invalid S3 uri")
        # workaround for this to work with localhost through full docker compose
        s3_url = str(self.s3_url)
        if s3_url.startswith("http://localstack"):
            s3_url = s3_url.replace("http://localstack", "http://localhost")
        bucket, key = uri[5:].split("/", 1)
        async with self.aio_session.client(
            "s3",
            endpoint_url=s3_url,
        ) as s3:
            url = await s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=3600,
            )
        return url


def get_storage():
    session = aioboto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION,
    )
    return Storage(
        aio_session=session,
        bucket_name=settings.BUCKET_NAME,
        s3_url=settings.S3_ENDPOINT_URL,
    )


StorageDep = Annotated[Storage, Depends(get_storage)]
