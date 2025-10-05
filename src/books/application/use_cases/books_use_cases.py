import uuid

from books.domain.entities.book_entities import DomainBook
from books.domain.entities.user_entities import DomainUser
from books.domain.exceptions.authors_exceptions import AuthorNotFoundException
from books.domain.exceptions.books_exceptions import (
    BookNotFoundException,
    TitleAuthorConstraintException,
)
from books.domain.protocols.auth.storage_protocols import StorageServiceProtocol
from books.domain.protocols.authors.db_protocols import AuthorsDBProtocol
from books.domain.protocols.books.db_protocols import BooksDBProtocol
from books.infra.mappers.books_mappers import BooksMapper
from books.presentation.schemas.books_schemas import BookReturnSchema, BooksInSchema


class BooksUseCase:
    def __init__(self, authors_db: AuthorsDBProtocol, books_db: BooksDBProtocol, storage: StorageServiceProtocol):
        self.authors_db = authors_db
        self.books_db = books_db
        self.storage = storage

    async def get_books(self, params: dict) -> tuple[int, list[BookReturnSchema]]:
        total_count = await self.books_db.get_books_count(params=params)
        books = [BooksMapper.domain_to_return_schema(book) for book in await self.books_db.get_books(params=params)]
        return total_count, books

    async def create_book(self, user: DomainUser, book_data: BooksInSchema) -> DomainBook:
        book_data_dict = book_data.model_dump()
        author_uid = book_data_dict.pop("author_uid")
        author = await self.authors_db.get_author_by_uid(author_uid=author_uid)
        if author is None:
            raise AuthorNotFoundException

        if image_uri := book_data_dict.pop("image_uri"):
            domain_image_file = self.storage.get_file_from_base64_uri(image_uri)
            file_url = await self.storage.save_file(file=domain_image_file)
        else:
            domain_image_file = None
            file_url = None

        domain_book = DomainBook(**book_data_dict, image=file_url, author=author)
        try:
            return await self.books_db.create_book(book=domain_book, created_by=user.uid)
        except TitleAuthorConstraintException:
            if domain_image_file:
                await self.storage.remove_file(filename=domain_image_file.filename)
            raise TitleAuthorConstraintException

    async def get_current_book(self, book_uid: uuid.UUID) -> DomainBook:
        current_book = await self.books_db.get_book_by_uid(book_uid=book_uid)
        if not current_book:
            raise BookNotFoundException
        return current_book

    async def update_book(self, user: DomainUser, book: DomainBook, update_data: dict) -> None:
        if author_uid := update_data.get("author_uid"):
            author = await self.authors_db.get_author_by_uid(author_uid)
            if author is None:
                raise AuthorNotFoundException

        if image_uri := update_data.get("image_uri"):
            update_data.pop("image_uri")
            domain_image_file = self.storage.get_file_from_base64_uri(image_uri)
            file_url = await self.storage.save_file(file=domain_image_file)
            update_data["image"] = file_url
        else:
            domain_image_file = None

        try:
            await self.books_db.update_book(book=book, update_data=update_data, updated_by=user.uid)
            if image_uri:
                await self.storage.remove_file(filename=self.storage.get_filename_from_url(url=book.image))
        except TitleAuthorConstraintException:
            if domain_image_file:
                await self.storage.remove_file(filename=domain_image_file.filename)
            raise TitleAuthorConstraintException

    async def delete_book(self, book: DomainBook) -> None:
        await self.books_db.delete_book(book=book)
        if book.image:
            await self.storage.remove_file(filename=self.storage.get_filename_from_url(url=book.image))
