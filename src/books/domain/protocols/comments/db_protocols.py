import uuid
from typing import Protocol

from books.domain.entities.book_entities import DomainBook
from books.domain.entities.comment_entities import DomainComment


class CommentsDBProtocol(Protocol):
    async def get_comments(self, book: DomainBook) -> list[DomainComment]:
        raise NotImplementedError

    async def create_comment(self, comment: DomainComment, created_by: uuid.UUID, book_uid: uuid.UUID) -> DomainComment:
        raise NotImplementedError

    async def get_comment_by_uid(self, comment_uid: uuid.UUID) -> DomainComment | None:
        raise NotImplementedError

    async def update_comment(self, comment: DomainComment, update_data: dict, updated_by: uuid.UUID) -> None:
        raise NotImplementedError

    async def delete_comment(self, comment: DomainComment) -> None:
        raise NotImplementedError
