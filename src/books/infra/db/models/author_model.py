from datetime import date

from sqlalchemy import Date, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from books.application.config import get_settings
from books.infra.db.models.base.base_model import BaseModel
from books.infra.db.models.mixins.model_mixins import (
    ByStampsMixin,
    TimestampsMixin,
    UIDMixin,
)


class Author(BaseModel, UIDMixin, TimestampsMixin, ByStampsMixin):
    first_name: Mapped[str] = mapped_column(String(get_settings().AUTHOR_NAME_MAX_LENGTH), nullable=False)
    last_name: Mapped[str] = mapped_column(String(get_settings().AUTHOR_NAME_MAX_LENGTH), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date(), nullable=False)
    bio: Mapped[str] = mapped_column(Text(), nullable=True)

    books = relationship("Book", back_populates="author")

    __table_args__ = (
        UniqueConstraint("first_name", "last_name", "birth_date", name="uq_first_name_last_name_birth_date"),
    )

    def __repr__(self):
        return f"{self.first_name.title()} {self.last_name.title()}"
