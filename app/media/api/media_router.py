from fastapi import APIRouter

from app.core.exceptions import InvalidStateException
from app.image_generator.storage import StorageDep
from app.media.api.schemas import MediaGenerationParams, MediaOut, MediaUrlOut
from app.media.job_id import JobId
from app.media.media_id import MediaId
from app.media.media_repository import MediaRepositoryDep
from app.media.media_status import MediaStatus
from app.tasks.celery_tasks import create_media

media_router = APIRouter()


@media_router.post("/generate", response_model=MediaOut)
async def generate(
    params: MediaGenerationParams,
    media_repository: MediaRepositoryDep,
):
    media = await media_repository.create_media(prompt=params.prompt)
    task = create_media.apply_async(kwargs={"media_id": media.id})
    return await media_repository.update_media_job_id(media.id, task.id)


@media_router.get("/status/{job_id}", response_model=MediaOut)
async def get_media(
    job_id: JobId,
    media_repository: MediaRepositoryDep,
):
    return await media_repository.get_from_job_id(job_id)


@media_router.get("/content/{media_id}", response_model=MediaUrlOut)
async def get_media_url(
    media_id: MediaId, storage: StorageDep, media_repository: MediaRepositoryDep
):
    media = await media_repository.get_or_raise(media_id)
    if media.status is not MediaStatus.COMPLETED:
        raise InvalidStateException(
            "media generation is not completed", extras=media.model_dump()
        )
    url = await storage.create_media_url(media.media_uri)
    return MediaUrlOut(url=url)
