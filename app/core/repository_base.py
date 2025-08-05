import json
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    TypeVar,
    Union,
    get_args,
)
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import (
    Table,
    insert,
    update,
    select,
    Row,
)
from sqlalchemy.orm import InstrumentedAttribute, Session

from app.core.database import (
    Base,
    SessionDep,
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
        session: SessionDep,
        async_session: AsyncSessionDep,
    ):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self._async_session: AsyncSessionLocal = async_session
        self._session = session
        generic_types = get_args(self.__orig_bases__[0])  # type: ignore

        self.model = generic_types[1]
        self.database_model = generic_types[0]
        if not issubclass(self.database_model, Basic):
            raise ValueError(
                f"model should be a subclass of {Base.__name__}, got {self.model}"
            )
        self.table: Table = self.database_model.__table__

    def get_or_raise(self, obj_id: Any) -> PydanticModelType:
        obj = self.get(obj_id)
        if obj is None:
            raise ResourceNotFoundException(
                f"Object with id {obj_id} does not exist",
                extras={"model": str(self.database_model)},
            )
        return obj

    def get_kwargs(self, **kwargs) -> PydanticModelType:
        obj = self.get_kwargs_maybe(**kwargs)
        if obj is None:
            raise ResourceNotFoundException(
                "Resource not found",
                extras={
                    "model": str(self.database_model),
                    "kwargs": jsonable_encoder(kwargs),
                },
            )
        return obj

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

    def get_all_kwargs(self, **kwargs) -> list[PydanticModelType]:
        query_results = (
            self._session.query(self.database_model).filter_by(**kwargs).all()
        )
        return [self._map_model(query_result) for query_result in query_results]

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

    def get_kwargs_maybe(self, **kwargs) -> PydanticModelType | None:
        query_result = (
            self._session.query(self.database_model).filter_by(**kwargs).first()
        )
        return self._map_optional_model(query_result)

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

    def get(self, obj_id: Any) -> Optional[PydanticModelType]:
        query_result = (
            self._session.query(self.database_model)
            .filter(self.database_model.id == obj_id)
            .first()
        )
        return self._map_optional_model(query_result)

    async def get_async(self, obj_id: Any):
        try:
            async with self._async_session() as session:
                query_result = await session.get(self.database_model, obj_id)
        except Exception as e:
            await session.rollback()
            raise e
        return self._map_optional_model(query_result)

    def create(self, obj_in: PydanticModelType) -> PydanticModelType:
        try:
            obj_in_data = obj_in.model_dump_json(exclude_none=True)
            db_obj = self.database_model(**json.loads(obj_in_data))
            self._session.add(db_obj)
            self._session.commit()
            self._session.refresh(db_obj)
        except Exception as e:
            self._session.rollback()
            raise e
        return self._map_model(db_obj)

    def remove_none_entries(self, input_dict: dict) -> dict:
        return {k: v for k, v in input_dict.items() if v is not None}

    def create_all(
        self, objs_in: Iterable[PydanticModelType] | Iterable[dict]
    ) -> List[PydanticModelType]:
        try:
            if not objs_in:
                return []
            db_objs = []
            for obj_in in objs_in:
                if isinstance(obj_in, dict):
                    db_objs.append(obj_in)
                else:
                    db_objs.append(jsonable_encoder(obj_in))
            new_objects = (
                self._session.scalars(
                    insert(self.database_model).returning(self.database_model), db_objs
                )
                .unique()
                .all()
            )
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise e
        return [self._map_model(db_obj) for db_obj in new_objects]

    def _map_to_database_model(self, obj_in: PydanticModelType) -> DatabaseModelType:
        return self.database_model(**jsonable_encoder(obj_in))

    def kwargs_create(self, **kwargs) -> PydanticModelType:
        try:
            db_obj = self.database_model(**kwargs)
            self._session.add(db_obj)
            self._session.commit()
            self._session.refresh(db_obj)
        except Exception as e:
            self._session.rollback()
            raise e
        return self._map_model(db_obj)

    async def kwargs_create_async(self, **kwargs) -> PydanticModelType:
        db_obj = self.database_model(**kwargs)
        try:
            async with self._async_session() as session:
                session.add(db_obj)
                await session.commit()
                await session.refresh(db_obj)
        except Exception as e:
            await session.rollback()
            raise e
        return self._map_model(db_obj)

    def kwargs_update(
        self,
        obj_id: UUID | None = None,
        session: Session = None,
        *,
        filters: BaseModel | dict | None = None,
        **kwargs,
    ) -> PydanticModelType:
        try:
            if obj_id is None and not filters:
                raise ValueError("obj_id or filters should be provided")

            filtered_kwargs = self.filter_kwargs_for_update(kwargs)
            current_session = session or self._session
            query = (
                update(self.database_model)
                .returning(self.database_model)
                .values(**filtered_kwargs)
            )

            if obj_id:
                query = query.where(self.database_model.id == obj_id)
            query = self._apply_filters(filters, query)

            result = current_session.execute(query)
            if session is None:
                self._session.commit()
            else:
                session.flush()

            updated_row = result.fetchone()
        except Exception as e:
            self._session.rollback()
            raise e
        if updated_row:
            return self._map_model(updated_row[0])
        else:
            raise ResourceNotFoundException(
                f"Object with id {obj_id} does not exist",
                extras={"model": str(self.database_model)},
            )

    def filter_kwargs_for_update(
        self, values: dict[str | InstrumentedAttribute, Any]
    ) -> dict[str, Any]:
        valid_columns = set(self.database_model.__table__.columns.keys())
        filtered_kwargs: dict[str:Any] = {}

        for key, value in values.items():
            str_key = key if isinstance(key, str) else key.key
            if str_key in valid_columns:
                filtered_kwargs[str_key] = value

        return filtered_kwargs

    async def kwargs_update_async(
        self,
        obj_id: UUID | None = None,
        *,
        filters: BaseModel | dict | None = None,
        **kwargs,
    ) -> PydanticModelType:
        if obj_id is None and not filters:
            raise ValueError("obj_id or filters should be provided")
        filtered_kwargs = self.filter_kwargs_for_update(kwargs)

        query = (
            update(self.database_model)
            .returning(self.database_model)
            .values(**filtered_kwargs)
        )

        if obj_id:
            query = query.where(self.database_model.id == obj_id)
        query = self._apply_filters(filters, query)

        try:
            async with self._async_session() as current_session:
                result = await current_session.execute(query)
                updated_row = result.fetchone()
                await current_session.commit()
        except Exception as e:
            await current_session.rollback()
            raise e
        if updated_row:
            return self._map_model(updated_row[0])
        else:
            raise ResourceNotFoundException(
                f"Object with id {obj_id} does not exist",
                extras={"model": str(self.database_model)},
            )

    def update(
        self,
        *,
        db_obj_id: Any,
        obj_in: Union[BaseModel, Dict[str, Any]],
    ) -> PydanticModelType:
        try:
            obj = self.object_to_dict(db_obj_id, obj_in)
            self._session.add(obj)
            self._session.commit()
            self._session.refresh(obj)
        except Exception as e:
            self._session.rollback()
            raise e
        return self._map_model(obj)

    def update_object(self, obj_in: PydanticModelType):
        try:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.database_model(**obj_in_data)
            self._session.merge(db_obj)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise e
        return self.get_or_raise(db_obj.id)

    def object_to_dict(self, db_obj_id, obj_in):
        obj = self._get(db_obj_id)
        if obj is None:
            raise ValueError(f"Object with id {db_obj_id} does not exist")
        obj_data = jsonable_encoder(obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            if isinstance(update_data[field], Iterable) and not isinstance(
                update_data[field], str
            ):
                objects = []
                for i, item in enumerate(update_data[field]):
                    if len(obj_data[field]) < i:
                        if isinstance(update_data[field][i], str) and not self.is_uuid(
                            update_data[field][i]
                        ):
                            objects.append(item)
                        else:
                            objects.append(
                                self.object_to_dict(obj_data[field][i], item)
                            )

                setattr(obj, field, objects)

            if isinstance(update_data[field], InstrumentedAttribute):
                setattr(
                    obj,
                    field,
                    self.object_to_dict(update_data[field], update_data[field].id),
                )
            if field in update_data:
                setattr(obj, field, update_data[field])
        return obj

    def _apply_filters(
        self,
        filters: BaseModel | dict[InstrumentedAttribute, Any] | None,
        query,
        exclude: set[InstrumentedAttribute] | None = None,
    ):
        if filters is not None:
            if isinstance(filters, dict):
                filters_dict = filters
            else:
                filters_dict = filters.model_dump(exclude_none=True, exclude=exclude)  # type: ignore
            for filter_name, filter_value in filters_dict.items():
                filter_name_string = str(filter_name)
                try:
                    if filter_name_string.index(".") > -1:
                        filter_name_string = filter_name_string.split(".")[1]
                except ValueError:
                    pass
                model_attribute = getattr(self.database_model, filter_name_string, None)
                if model_attribute is not None:
                    query = query.filter(model_attribute == filter_value)
        return query

    def _get(self, obj_id: Any) -> Optional[DatabaseModelType]:
        return self._session.get(self.database_model, obj_id)

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

    def kwargs_count(self, **kwargs) -> int:
        return self._session.query(self.database_model).filter_by(**kwargs).count()

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

    def execute_text(self, sql_text):
        result = self._session.execute(sql_text)
        return result.scalars().all()
