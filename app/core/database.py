import asyncio
from typing import Any, Annotated

from fastapi import Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    TIMESTAMP,
    Column,
    Table,
    create_engine,
    func,
    inspect,
    Engine,
)
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import as_declarative, sessionmaker, Session

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


SessionLocal = Session
AsyncSessionLocal = async_sessionmaker[AsyncSession]


class DatabaseConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    engine: Engine | None = None
    async_engine: AsyncEngine | None = None
    session_local: sessionmaker[Session] | None = None
    async_session_local: async_sessionmaker[AsyncSession] | None = None


def get_database_config():
    engine = create_engine(
        str(settings.SQLALCHEMY_DATABASE_URI),
        pool_size=10,  # Set the number of connections in the pool
        max_overflow=20,  # Set the maximum overflow size
        pool_timeout=30,  # Set the timeout for getting a connection from the pool
        pool_recycle=1800,  # Set the recycle time for connections
        # echo=True,  # Set the logging level
        connect_args={"application_name": "fleek-backend-sync"},
    )
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    async_engine = create_async_engine(
        str(settings.ASYNC_SQLALCHEMY_DATABASE_URI),
        pool_size=11,  # Set the number of connections in the pool
        max_overflow=20,  # Set the maximum overflow size
        pool_timeout=30,  # Set the timeout for getting a connection from the pool
        pool_recycle=1800,  # Set the recycle time for connections
        # echo=True,  # Set the logging level
        connect_args={
            "application_name": "fleek-backend-async",
            # "options": "-c idle_in_transaction_session_timeout=30000",
        },
    )

    async_session_local = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    return DatabaseConfig(
        engine=engine,
        async_engine=async_engine,
        session_local=SessionLocal,
        async_session_local=async_session_local,
    )


database_config = get_database_config()


def get_async_db():
    return database_config.async_session_local


def get_db():
    with database_config.session_local() as db:
        yield db
    

SessionDep = Annotated[Session, Depends(get_db)]
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_db)]
