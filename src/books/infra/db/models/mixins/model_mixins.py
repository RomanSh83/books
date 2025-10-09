import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class UIDMixin:
    uid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class CreateMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UpdateMixin:
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_onupdate=func.now(), server_default=func.now()
    )


class TimestampsMixin(CreateMixin, UpdateMixin):
    pass


class ByStampsMixin:
    @declared_attr
    def created_by(cls) -> Mapped[uuid.UUID]:
        return mapped_column(
            ForeignKey("user.uid", name=f"fk_{cls.__tablename__}_created_by_user_uid"),  # type: ignore
            nullable=False,
        )

    @declared_attr
    def updated_by(cls) -> Mapped[uuid.UUID]:
        return mapped_column(
            ForeignKey("user.uid", name=f"fk_{cls.__tablename__}_updated_by_user_uid"),  # type: ignore
            default=None,
            nullable=True,
        )
