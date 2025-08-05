from pydantic import AnyUrl

from app.core.model import Model
from app.media.job_id import JobId
from app.media.media_id import MediaId
from app.media.media_status import MediaStatus


class Media(Model):
    id: MediaId
    job_id: JobId | None = None
    prompt: str
    status: MediaStatus
    media_uri: AnyUrl | None = None
