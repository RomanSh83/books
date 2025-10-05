from uuid import UUID

from sqlalchemy import String, Text, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from books.application.config import get_settings
from books.infra.db.models.base.base_model import BaseModel
from books.infra.db.models.mixins.model_mixins import UIDMixin, TimestampsMixin, ByStampsMixin


class Comment(BaseModel, UIDMixin, TimestampsMixin, ByStampsMixin):
    book_uid: Mapped[UUID] = mapped_column(ForeignKey("book.uid"), nullable=False)
    text: Mapped[str] = mapped_column(Text(), nullable=False)

    book = relationship("Book", back_populates="comments")

    def __repr__(self):
        return f"{self.text}"