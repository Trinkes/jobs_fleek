from uuid import UUID

from pydantic import Json

from app.core.model import Model
from app.logs.log_level import LogLevel


class Log(Model):
    id: UUID
    tag: str
    level: LogLevel
    extra: Json
    message: str
