from fastapi import APIRouter

from app.media.api.schemas import MediaGenerationParams, MediaOut
from app.media.media_repository import MediaRepositoryDep
from app.tasks.celery_tasks import create_media

media_router = APIRouter()


@media_router.post("/generate", response_model=MediaOut)
async def generate(
    params: MediaGenerationParams,
    media_repository: MediaRepositoryDep,
):
    media = media_repository.kwargs_create(prompt=params.prompt)
    task = create_media.apply_async(kwargs={"media_id": media.id})
    return await media_repository.update_media_job_id(media.id, task.id)
