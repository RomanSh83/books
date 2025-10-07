from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from books.infra.db.models.base.base_model import BaseModel
from books.infra.db.models.mixins.model_mixins import (
    TimestampsMixin,
    UIDMixin,
)


class Rating(BaseModel, UIDMixin, TimestampsMixin):
    user_uid: Mapped[UUID] = mapped_column(
        ForeignKey("user.uid", name="fk_rating_user_uid"), nullable=False, primary_key=True
    )
    book_uid: Mapped[UUID] = mapped_column(
        ForeignKey("book.uid", name="fk_rating_book_uid"), nullable=False, primary_key=True
    )
    points: Mapped[int] = mapped_column(Integer(), nullable=False)

    book = relationship("Book", back_populates="rating")
