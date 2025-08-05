from typing import (
    Any,
    Generic,
    TypeVar,
    get_args,
)
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import (
    Table,
    select,
    Row,
)

from app.core.database import (
    Base,
    AsyncSessionDep,
    AsyncSessionLocal,
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
        self._async_session: AsyncSessionLocal = async_session
        generic_types = get_args(self.__orig_bases__[0])  # type: ignore

        self.model = generic_types[1]
        self.database_model = generic_types[0]
        if not issubclass(self.database_model, Basic):
            raise ValueError(
                f"model should be a subclass of {Base.__name__}, got {self.model}"
            )
        self.table: Table = self.database_model.__table__

    async def get_kwargs_async(self, **kwargs) -> PydanticModelType:
        obj = await self.get_kwargs_maybe_async(**kwargs)
        if obj is None:
            raise ResourceNotFoundException(
                "Resource not found",
                extras={
                    "model": str(self.database_model),
                    "kwargs": jsonable_encoder(kwargs),
                },
            )
        return obj

    async def get_all_kwargs_async(self, **kwargs) -> list[PydanticModelType]:
        try:
            async with self._async_session() as session:
                results = (
                    await session.execute(
                        select(self.database_model).filter_by(**kwargs)
                    )
                ).all()
        except Exception as e:
            await session.rollback()
            raise e
        return [self._map_model(result[0]) for result in results]

    async def get_kwargs_maybe_async(self, **kwargs) -> PydanticModelType | None:
        try:
            async with self._async_session() as session:
                result = (
                    await session.execute(
                        select(self.database_model).filter_by(**kwargs)
                    )
                ).one_or_none()
                query_result = result[0] if result else None
        except Exception as e:
            await session.rollback()
            raise e

        return self._map_optional_model(query_result)

    async def get_or_raise(self, obj_id: Any) -> PydanticModelType:
        async with self._async_session() as session:
            query_result = await session.get(self.database_model, obj_id)
        return self._map_optional_model(query_result)

    def _map_model(self, model: DatabaseModelType | None) -> PydanticModelType:
        optional_model = self._map_optional_model(model)
        if optional_model is None:
            raise ResourceNotFoundException(
                "Model is None", extras={"model": str(self.database_model)}
            )
        else:
            return optional_model

    def _map_optional_model(
        self, model: DatabaseModelType | None
    ) -> PydanticModelType | None:
        if isinstance(model, Row):
            model = model[0]
        if model is None:
            return None
        return self.model.model_validate(model)

    def is_uuid(self, text: str) -> bool:
        try:
            UUID(text)
            return True
        except ValueError:
            return False

    def map_models(
        self, models: list[DatabaseModelType | Row]
    ) -> list[PydanticModelType]:
        to_return = []
        for model in models:
            if isinstance(model, Row):
                model = model[0]
            to_return.append(self._map_model(model))

        return to_return

    async def execute_async(self, sql_text):
        try:
            async with self._async_session() as session:
                result = await session.execute(sql_text)
        except Exception as e:
            await session.rollback()
            raise e
        return result.scalars().all()
