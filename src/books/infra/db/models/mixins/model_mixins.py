import uuid
from datetime import datetime

from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UIDMixin:
    uid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

class CreateMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class UpdateMixin:
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_onupdate=func.now(), server_default=func.now())

class TimestampsMixin(CreateMixin, UpdateMixin):
    pass

class ByStampsMixin:
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.uid"), nullable=False)
    updated_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.uid"), nullable=True)