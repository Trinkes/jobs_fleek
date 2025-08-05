from typing import Annotated

from fastapi import Depends
from sqlalchemy import update

from app.core.repository_base import BaseRepository
from app.media.db_media import Medias
from app.media.job_id import JobId
from app.media.media import Media
from app.media.media_id import MediaId


class MediaRepository(BaseRepository[Medias, Media]):
    async def update_media_job_id(self, media_id: MediaId, job_id: JobId):
        async with self._async_session() as session:
            statement = (
                update(Medias)
                .where(Medias.id == media_id)
                .values(job_id=job_id)
                .returning(Medias)
            )
            media = (await session.execute(statement)).fetchone()
            return self._map_model(media)


MediaRepositoryDep = Annotated[MediaRepository, Depends()]
