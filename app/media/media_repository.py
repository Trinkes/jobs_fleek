from typing import Annotated

from fastapi import Depends
from sqlalchemy import update, Row, select

from app.core.repository_base import BaseRepository, PydanticModelType
from app.media.db_media import Medias
from app.media.job_id import JobId
from app.media.media import Media, Status
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
            await session.commit()
            return self._map_model(media)

    def _map_optional_model(self, model: Medias | None) -> PydanticModelType | None:
        if isinstance(model, Row):
            model = model[0]
        if model is None:
            return None
        return Media(
            id=model.id,
            status=Status(
                job_id=model.job_id,
                status=model.status,
            ),
            prompt=model.prompt,
        )

    async def get_from_job_id(self, job_id: JobId) -> Media:
        async with self._async_session() as session:
            statement = select(Medias).where(Medias.job_id == job_id)
            media = (await session.execute(statement)).fetchone()
            return self._map_model(media)


MediaRepositoryDep = Annotated[MediaRepository, Depends()]
