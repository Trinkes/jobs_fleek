from abc import ABC, abstractmethod
from datetime import datetime

from app.media.job_id import JobId
from app.media.media_id import MediaId


class TaskScheduler(ABC):
    @abstractmethod
    def schedule_media_generation(self, media_id: MediaId, eta: datetime) -> JobId:
        raise NotImplementedError()
