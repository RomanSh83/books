import uuid
from typing import Protocol

from books.domain.entities.book_entities import DomainBook


class BooksDBProtocol(Protocol):
    async def get_books(self, params: dict) -> list[DomainBook]:
        raise NotImplementedError

    async def get_books_count(self, params: dict) -> int:
        raise NotImplementedError

    async def create_book(self, book: DomainBook, created_by: uuid.UUID) -> DomainBook:
        raise NotImplementedError

    async def get_book_by_uid(self, book_uid: uuid.UUID) -> DomainBook | None:
        raise NotImplementedError

    async def update_book(self, book: DomainBook, update_data: dict, updated_by: uuid.UUID) -> None:
        raise NotImplementedError

    async def delete_book(self, book: DomainBook) -> None:
        raise NotImplementedError
