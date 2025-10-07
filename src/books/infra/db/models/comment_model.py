from uuid import UUID

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from books.infra.db.models.base.base_model import BaseModel
from books.infra.db.models.mixins.model_mixins import (
    ByStampsMixin,
    TimestampsMixin,
    UIDMixin,
)


class Comment(BaseModel, UIDMixin, TimestampsMixin, ByStampsMixin):
    book_uid: Mapped[UUID] = mapped_column(ForeignKey("book.uid", name="fk_comment_book_uid"), nullable=False)
    text: Mapped[str] = mapped_column(Text(), nullable=False)

    book = relationship("Book", back_populates="comments")

    def __repr__(self):
        return f"{self.text}"
