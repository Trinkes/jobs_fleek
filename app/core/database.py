from typing import Any, Annotated

from fastapi import Depends
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


async_engine = None
AsyncSessionLocal = None


def setup_database():
    global async_engine, AsyncSessionLocal
    async_engine = create_async_engine(f"{settings.ASYNC_SQLALCHEMY_DATABASE_URI}")
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    return AsyncSessionLocal


def get_engine():
    if async_engine is None:
        raise ValueError(
            "you must call setup_database function before using database sessions"
        )
    return async_engine


def get_db():
    if AsyncSessionLocal is None:
        raise ValueError(
            "you must call setup_database function before using database sessions"
        )
    return AsyncSessionLocal


AsyncSessionDep = Annotated[async_sessionmaker[AsyncSession], Depends(get_db)]
