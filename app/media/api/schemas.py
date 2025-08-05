from app.core.model import BasicModel
from app.media.job_id import JobId
from app.media.media_status import MediaStatus


class MediaGenerationParams(BasicModel):
    prompt: str


class MediaOut(BasicModel):
    id: JobId
    job_id: JobId
    prompt: str
    status: MediaStatus
