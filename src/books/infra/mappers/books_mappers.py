from dataclasses import asdict

from books.domain.entities.book_entities import DomainBook
from books.infra.db.models.book_model import Book as ORMBook
from books.infra.mappers.authors_mappers import AuthorsMapper
from books.presentation.schemas.books_schemas import BookReturnSchema


class BooksMapper:
    @staticmethod
    def orm_to_domain(book: ORMBook) -> DomainBook:
        return DomainBook(
            uid=book.uid,
            title=book.title,
            author=AuthorsMapper.orm_to_domain(book.author),
            published_year=book.published_year,
            description=book.description,
            image=book.image,
        )

    @staticmethod
    def domain_to_return_schema(book: DomainBook) -> BookReturnSchema:
        return BookReturnSchema(**asdict(book))
