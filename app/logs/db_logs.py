import uuid

from sqlalchemy import JSON, Column, Enum, String, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.logs.log_level import LogLevel


class Logs(Base):
    __tablename__ = "logs"
    id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    tag: Mapped[str] = mapped_column(String, index=True, nullable=False)
    level: Mapped[LogLevel] = mapped_column(Enum(LogLevel), default=LogLevel.DEBUG)
    message: str = Column(String, nullable=True)
    extra: dict = Column(JSON, nullable=True)
