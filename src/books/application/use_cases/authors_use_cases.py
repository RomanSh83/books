import uuid

from books.domain.entities.author_entities import DomainAuthor
from books.domain.entities.user_entities import DomainUser
from books.domain.exceptions.authors_exceptions import AuthorNotFoundException
from books.domain.protocols.authors.db_protocols import AuthorsDBProtocol
from books.presentation.schemas.authors_shemas import AuthorInSchema


class AuthorsUseCase:
    def __init__(self, db: AuthorsDBProtocol):
        self.db = db

    async def get_authors(self) -> list[DomainAuthor]:
        return await self.db.get_authors()

    async def create_author(self, user: DomainUser, author_data: AuthorInSchema) -> DomainAuthor:
        domain_author = DomainAuthor(**author_data.model_dump())
        return await self.db.create_author(author=domain_author, created_by=user.uid)

    async def get_current_author(self, author_uid: uuid.UUID) -> DomainAuthor:
        current_author = await self.db.get_author_by_uid(author_uid=author_uid)
        if not current_author:
            raise AuthorNotFoundException
        return current_author

    async def update_author(self, user: DomainUser, author: DomainAuthor, update_data: dict) -> None:
        await self.db.update_author(author=author, update_data=update_data, updated_by=user.uid)

    async def delete_author(self, author: DomainAuthor) -> None:
        await self.db.delete_author(author=author)
