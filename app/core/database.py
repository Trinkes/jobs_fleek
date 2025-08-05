from typing import Any, Annotated

from fastapi import Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    TIMESTAMP,
    Column,
    Table,
    func,
    inspect,
)
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import as_declarative

from app.core.config import settings


@as_declarative()
class Basic:
    __table__: Table

    def __repr__(self):
        return repr(self.__dict__)

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class Base(Basic):
    __abstract__ = True

    id: Any
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    def __repr__(self):
        return repr(self.__dict__)

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


AsyncSessionLocal = async_sessionmaker[AsyncSession]


class DatabaseConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    async_engine: AsyncEngine | None = None
    async_session_local: async_sessionmaker[AsyncSession] | None = None


def get_database_config():
    async_engine = create_async_engine(
        f"{settings.ASYNC_SQLALCHEMY_DATABASE_URI}",
        # echo=True,
    )

    async_session_local = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    return DatabaseConfig(
        async_engine=async_engine,
        async_session_local=async_session_local,
    )


database_config = get_database_config()


def get_async_db():
    return database_config.async_session_local


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_db)]
