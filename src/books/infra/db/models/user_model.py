from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from books.infra.db.models.base.base_model import BaseModel
from books.infra.db.models.mixins.model_mixins import UIDMixin, TimestampsMixin


class User(BaseModel, UIDMixin, TimestampsMixin):
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_activated: Mapped[bool] = mapped_column(Boolean(), default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean(), default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean(), default=False)