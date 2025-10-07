import uuid
from typing import Protocol


class RatingsDBProtocol(Protocol):
    async def rate_book(self, points: int, user_uid: uuid.UUID, book_uid: uuid.UUID) -> None:
        raise NotImplementedError

    async def get_book_rating(self, book_uid: uuid.UUID) -> float | None:
        raise NotImplementedError
