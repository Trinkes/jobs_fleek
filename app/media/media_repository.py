from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import update, select

from app.core.repository_base import BaseRepository
from app.media.db_media import Medias
from app.media.job_id import JobId
from app.media.media import Media
from app.media.media_id import MediaId
from app.media.media_status import MediaStatus


class MediaRepository(BaseRepository[Medias, Media]):
    async def update_media_job_id(self, media_id: MediaId, job_id: JobId):
        async with self._async_session() as session:
            statement = (
                update(Medias)
                .where(Medias.id == media_id)
                .values(**{Medias.job_id.key: job_id, Medias.celery_jobs.key: [job_id]})
                .returning(Medias)
            )
            media = (await session.execute(statement)).fetchone()
            await session.commit()
            return self._map_model(media)

    async def get_from_job_id(self, job_id: JobId) -> Media:
        async with self._async_session() as session:
            statement = select(Medias).where(Medias.job_id == job_id)
            media = (await session.execute(statement)).fetchone()
            return self._map_model(media)

    async def finish_media_generation(
        self, media_id: MediaId, image_uri: str, status: MediaStatus
    ) -> Media:
        statement = (
            update(Medias)
            .where(Medias.id == media_id)
            .values(
                **{
                    Medias.media_uri.key: image_uri,
                    Medias.status.key: status,
                    Medias.number_of_tries.key: Medias.number_of_tries + 1,
                }
            )
            .returning(Medias)
        )
        async with self._async_session() as session:
            media = (await session.execute(statement)).fetchone()
            await session.commit()
            return self._map_model(media)

    async def create_media(self, prompt: str) -> Media:
        async with self._async_session() as session:
            medias = Medias(prompt=prompt)
            session.add(medias)
            await session.commit()
            return self._map_model(medias)

    async def get_and_update_status(
        self,
        media_id: MediaId,
        required_status: MediaStatus,
        status_to_update: MediaStatus,
    ) -> Media:
        statement = (
            update(Medias)
            .where(Medias.id == media_id, Medias.status == required_status)
            .values(**{Medias.status.key: status_to_update})
            .returning(Medias)
        )
        async with self._async_session() as session:
            media = (await session.execute(statement)).fetchone()
            await session.commit()
            return self._map_model(media)

    async def register_media_generation_error(
        self,
        media_id: MediaId,
        next_run: datetime | None,
        new_job_id: JobId | None,
        status: MediaStatus,
    ):
        values = {
            Medias.status.key: status,
            Medias.next_run.key: next_run,
            Medias.number_of_tries.key: Medias.number_of_tries + 1,
            Medias.celery_jobs.key: Medias.celery_jobs + [new_job_id],
        }
        statement = (
            update(Medias)
            .where(Medias.id == media_id)
            .values(**values)
            .returning(Medias)
        )
        async with self._async_session() as session:
            media = (await session.execute(statement)).fetchone()
            await session.commit()
            return self._map_model(media)


MediaRepositoryDep = Annotated[MediaRepository, Depends()]
