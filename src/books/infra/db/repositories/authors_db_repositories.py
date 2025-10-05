import uuid
from dataclasses import asdict

from sqlalchemy import delete, exists, insert, select, update
from sqlalchemy.exc import IntegrityError

from books.domain.entities.author_entities import DomainAuthor
from books.domain.exceptions.authors_exceptions import (
    FirstLastNameBirthDateConstraintException,
)
from books.domain.protocols.authors.db_protocols import AuthorsDBProtocol
from books.infra.db.adapter.postgre_adapter import PostgresAdapter
from books.infra.db.models.author_model import Author as DBAuthor
from books.infra.mappers.authors_mappers import AuthorsMapper


class AuthorsDBRepository(AuthorsDBProtocol):
    def __init__(self, db_adapter: PostgresAdapter):
        self.db_adapter = db_adapter

    async def get_authors(self) -> list[DomainAuthor]:
        query = select(DBAuthor).order_by(DBAuthor.last_name, DBAuthor.first_name)
        async with self.db_adapter.get_session() as session:
            results = await session.scalars(query)
        return [AuthorsMapper.orm_to_domain(author) for author in results]

    async def create_author(self, author: DomainAuthor, created_by: uuid.UUID) -> DomainAuthor:
        author_data = asdict(author)
        author_data.pop("uid")
        query = (
            insert(DBAuthor)
            .values(**author_data, created_by=created_by)
            .returning(DBAuthor.uid, DBAuthor.first_name, DBAuthor.last_name, DBAuthor.birth_date, DBAuthor.bio)
        )
        async with self.db_adapter.get_session() as session:
            try:
                result = await session.execute(query)
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise FirstLastNameBirthDateConstraintException
        return DomainAuthor(**result.mappings().first())

    async def get_author_by_uid(self, author_uid: uuid.UUID) -> DomainAuthor | None:
        query = select(DBAuthor).where(DBAuthor.uid == author_uid)
        async with self.db_adapter.get_session() as session:
            result = await session.execute(query)
        author = result.scalar_one_or_none()
        if author:
            return AuthorsMapper.orm_to_domain(author)
        return None

    async def is_exists_author(self, author_uid: uuid.UUID) -> bool:
        query = select(exists().where(DBAuthor.uid == author_uid))
        async with self.db_adapter.get_session() as session:
            result = await session.execute(query)
        return result.scalar()

    async def update_author(self, author: DomainAuthor, update_data: dict, updated_by: uuid.UUID) -> None:
        query = update(DBAuthor).where(DBAuthor.uid == author.uid).values(**update_data, updated_by=updated_by)
        async with self.db_adapter.get_session() as session:
            try:
                await session.execute(query)
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise FirstLastNameBirthDateConstraintException

    async def delete_author(self, author: DomainAuthor) -> None:
        query = delete(DBAuthor).where(DBAuthor.uid == author.uid)
        async with self.db_adapter.get_session() as session:
            await session.execute(query)
            await session.commit()
