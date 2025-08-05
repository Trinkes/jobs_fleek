import uuid

from sqlalchemy import UUID, String, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.media.media_status import MediaStatus


class Medias(Base):
    __tablename__ = "medias"
    __table_args__ = (
        UniqueConstraint(
            "job_id",
            name="job_id_unique",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), index=True, default=uuid.uuid4
    )
    prompt: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[MediaStatus] = mapped_column(
        Enum(MediaStatus, native_enum=False),
        nullable=False,
        default=MediaStatus.IN_QUEUE,
    )

    media_uri: Mapped[str] = mapped_column(String, nullable=True)
