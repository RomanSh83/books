from books.domain.entities.book_entities import DomainBook
from books.domain.entities.user_entities import DomainUser
from books.domain.exceptions.ratings_exceptions import BookNotRatedException
from books.domain.protocols.ratings.db_protocols import RatingsDBProtocol
from books.presentation.schemas.ratings_schemas import RatingReturnSchema


class RatingsUseCase:
    def __init__(self, db: RatingsDBProtocol):
        self.db = db

    async def rate_book(self, points: int, user: DomainUser, book: DomainBook) -> None:
        await self.db.rate_book(points=points, user_uid=user.uid, book_uid=book.uid)

    async def get_rating(self, book: DomainBook) -> RatingReturnSchema:
        rating = await self.db.get_book_rating(book_uid=book.uid)
        if not rating:
            raise BookNotRatedException
        return RatingReturnSchema(rating=rating)
