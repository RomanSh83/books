from uuid import UUID

from sqlalchemy import String, Text, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from books.application.config import get_settings
from books.infra.db.models.base.base_model import BaseModel
from books.infra.db.models.mixins.model_mixins import UIDMixin, TimestampsMixin, ByStampsMixin


class Book(BaseModel, UIDMixin, TimestampsMixin, ByStampsMixin):
    title: Mapped[str] = mapped_column(String(get_settings().BOOK_TITLE_MAX_LENGTH), nullable=False)
    author_uid: Mapped[UUID] = mapped_column(ForeignKey("author.uid"), nullable=False)
    published_year: Mapped[int] = mapped_column(Integer(), nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=False)
    image: Mapped[str] = mapped_column(String(64), nullable=True)

    author = relationship("Author", back_populates="books")
    comments = relationship("Comment", back_populates="book")

    __table_args__ = (
        UniqueConstraint("title", "author_uid"),
    )

    def __repr__(self):
        return f"{self.title.title()}"
