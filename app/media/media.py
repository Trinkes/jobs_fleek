from app.core.model import Model, BasicModel
from app.media.job_id import JobId
from app.media.media_id import MediaId
from app.media.media_status import MediaStatus


class Status(BasicModel):
    job_id: JobId | None = None
    status: MediaStatus


class Media(Model):
    id: MediaId
    status: Status
    prompt: str
