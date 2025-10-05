import uuid
from typing import Protocol

from books.domain.entities.author_entities import DomainAuthor


class AuthorsDBProtocol(Protocol):
    async def get_authors(self) -> list[DomainAuthor]:
        raise NotImplementedError

    async def create_author(self, author: DomainAuthor, created_by: uuid.UUID) -> DomainAuthor:
        raise NotImplementedError

    async def get_author_by_uid(self, author_uid: uuid.UUID) -> DomainAuthor | None:
        raise NotImplementedError

    async def is_exists_author(self, author_uid: uuid.UUID) -> bool:
        raise NotImplementedError

    async def update_author(self, author: DomainAuthor, update_data: dict, updated_by: uuid.UUID) -> None:
        raise NotImplementedError

    async def delete_author(self, author: DomainAuthor) -> None:
        raise NotImplementedError
