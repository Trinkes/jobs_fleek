from fastapi import APIRouter

from app.media.api.schemas import MediaGenerationParams, MediaOut
from app.media.job_id import JobId
from app.media.media_repository import MediaRepositoryDep
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
