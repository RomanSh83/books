import uuid

from sqlalchemy import func, insert, select
from sqlalchemy.exc import IntegrityError

from books.domain.exceptions.ratings_exceptions import BookAlreadyRatedException
from books.domain.protocols.ratings.db_protocols import RatingsDBProtocol
from books.infra.db.adapter.postgre_adapter import PostgresAdapter
from books.infra.db.models.rating_model import Rating as DBRating


class RatingsDBRepository(RatingsDBProtocol):
    def __init__(self, db_adapter: PostgresAdapter):
        self.db_adapter = db_adapter

    async def rate_book(self, points: int, user_uid: uuid.UUID, book_uid: uuid.UUID) -> None:
        query = insert(DBRating).values(points=points, user_uid=user_uid, book_uid=book_uid)
        async with self.db_adapter.get_session() as session:
            try:
                await session.execute(query)
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise BookAlreadyRatedException

    async def get_book_rating(self, book_uid: uuid.UUID) -> float | None:
        query = select(func.round(func.avg(DBRating.points), 2)).where(DBRating.book_uid == book_uid)
        async with self.db_adapter.get_session() as session:
            result = await session.scalar(query)
        return result
