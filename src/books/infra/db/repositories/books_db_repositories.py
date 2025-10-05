import uuid
from dataclasses import asdict

from sqlalchemy import Select, delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from books.domain.entities.author_entities import DomainAuthor
from books.domain.entities.book_entities import DomainBook
from books.domain.exceptions.books_exceptions import TitleAuthorConstraintException
from books.domain.protocols.books.db_protocols import BooksDBProtocol
from books.infra.db.adapter.postgre_adapter import PostgresAdapter
from books.infra.db.models.book_model import Book as DBBook
from books.infra.mappers.books_mappers import BooksMapper


class BooksDBRepository(BooksDBProtocol):
    def __init__(self, db_adapter: PostgresAdapter):
        self.db_adapter = db_adapter

    @staticmethod
    def _filter_by_params(query: Select, params: dict) -> Select:
        if title := params["title"]:
            query = query.where(DBBook.title.ilike(f"%{title}%"))
        if author := params["author"]:
            if isinstance(author, str):
                query = query.where(DBBook.author.last_name.ilike(f"%{author}%"))
            elif isinstance(author, uuid.UUID):
                query = query.where(DBBook.author.uid == author)
        return query

    async def get_books(self, params: dict) -> list[DomainBook]:
        query = select(DBBook).options(joinedload(DBBook.author)).order_by(DBBook.title)
        query = self._filter_by_params(query=query, params=params)
        query = query.limit(params["limit"]).offset(params["offset"])
        async with self.db_adapter.get_session() as session:
            results = await session.scalars(query)
        return [BooksMapper.orm_to_domain(book) for book in results]

    async def get_books_count(self, params: dict) -> int:
        query = select(func.count(DBBook.uid)).select_from(DBBook)
        query = self._filter_by_params(query=query, params=params)
        async with self.db_adapter.get_session() as session:
            result = await session.scalar(query)
        return result

    async def create_book(self, book: DomainBook, created_by: uuid.UUID) -> DomainBook:
        book_data = asdict(book)
        book_data.pop("uid")
        author = book_data.pop("author")
        query = (
            insert(DBBook)
            .values(**book_data, author_uid=author["uid"], created_by=created_by)
            .returning(DBBook.uid, DBBook.title, DBBook.published_year, DBBook.description, DBBook.image)
        )
        async with self.db_adapter.get_session() as session:
            try:
                result = await session.execute(query)
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise TitleAuthorConstraintException
        return DomainBook(**result.mappings().first(), author=DomainAuthor(**author))

    async def get_book_by_uid(self, book_uid: uuid.UUID) -> DomainBook | None:
        query = select(DBBook).options(joinedload(DBBook.author)).where(DBBook.uid == book_uid)
        async with self.db_adapter.get_session() as session:
            result = await session.execute(query)
        book = result.scalar_one_or_none()
        if book:
            return BooksMapper.orm_to_domain(book)
        return None

    async def update_book(self, book: DomainBook, update_data: dict, updated_by: uuid.UUID) -> None:
        query = update(DBBook).where(DBBook.uid == book.uid).values(**update_data, updated_by=updated_by)
        async with self.db_adapter.get_session() as session:
            try:
                await session.execute(query)
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise TitleAuthorConstraintException

    async def delete_book(self, book: DomainBook) -> None:
        query = delete(DBBook).where(DBBook.uid == book.uid)
        async with self.db_adapter.get_session() as session:
            await session.execute(query)
            await session.commit()
