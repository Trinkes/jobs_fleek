from typing import (
    Generic,
    TypeVar,
    get_args,
)
from uuid import UUID

from sqlalchemy import (
    Table,
    Row,
)

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import (
    Base,
    AsyncSessionDep,
    Basic,
)
from app.core.exceptions import ResourceNotFoundException
from app.core.model import Model

DatabaseModelType = TypeVar("DatabaseModelType", bound=Base)  # pylint: disable=C0103
PydanticModelType = TypeVar("PydanticModelType", bound=Model)  # pylint: disable=C0103


class BaseRepository(Generic[DatabaseModelType, PydanticModelType]):
    def __init__(
        self,
        async_session: AsyncSessionDep,
    ):
        self._async_session: async_sessionmaker[AsyncSession] = async_session
        generic_types = get_args(self.__orig_bases__[0])  # type: ignore

        self.model = generic_types[1]
        self.database_model = generic_types[0]
        if not issubclass(self.database_model, Basic):
            raise ValueError(
                f"model should be a subclass of {Base.__name__}, got {self.model}"
            )
        self.table: Table = self.database_model.__table__

    async def get_or_raise(self, object_id: UUID) -> PydanticModelType:
        async with self._async_session() as session:
            model = await session.get(self.database_model, object_id)
            return self._map_model(model)

    def _map_model(
        self, model: DatabaseModelType | Row[tuple[DatabaseModelType]] | None
    ) -> PydanticModelType:
        optional_model = self._map_optional_model(model)
        if optional_model is None:
            raise ResourceNotFoundException(
                "Model is None", extras={"model": str(self.database_model)}
            )
        else:
            return optional_model

    def _map_optional_model(
        self, model: DatabaseModelType | Row[tuple[DatabaseModelType]] | None
    ) -> PydanticModelType | None:
        if isinstance(model, Row):
            model = model[0]
        if model is None:
            return None
        return self.model.model_validate(model)
