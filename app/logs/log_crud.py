from typing import Annotated

from fastapi import Depends

from app.core.repository_base import BaseRepository
from app.logs.db_logs import Logs
from app.logs.json_serializable import make_json_serializable
from app.logs.log import Log
from app.logs.log_level import LogLevel


class LogsRepository(BaseRepository[Logs, Log]):
    async def log(
        self,
        tag: str,
        level: LogLevel | None = None,
        message: str | None = None,
        extra: dict | None = None,
    ) -> None:
        async with self._async_session() as session:
            logs = Logs(
                tag=tag,
                level=level,
                extra=make_json_serializable(extra),
                message=message,
            )
            session.add(logs)
            await session.commit()


LogRepositoryDep = Annotated[LogsRepository, Depends()]
