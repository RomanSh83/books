import uuid
from typing import Annotated

from fastapi import Depends, HTTPException
from starlette import status

from books.application.use_cases.books_use_cases import BooksUseCase
from books.domain.entities.book_entities import DomainBook
from books.domain.exceptions.books_exceptions import BookNotFoundException
from books.infra.db.adapter.postgre_adapter import PostgresAdapter, get_db_adapter
from books.infra.db.repositories.authors_db_repositories import AuthorsDBRepository
from books.infra.db.repositories.books_db_repositories import BooksDBRepository
from books.infra.storage.repositories.storage_service import StorageService


def get_books_uc(
    db_adapter: Annotated[PostgresAdapter, Depends(get_db_adapter)],
):
    authors_db = AuthorsDBRepository(db_adapter=db_adapter)
    books_db = BooksDBRepository(db_adapter=db_adapter)
    storage = StorageService()

    return BooksUseCase(authors_db=authors_db, books_db=books_db, storage=storage)


async def get_current_book(book_id: uuid.UUID, books_uc: Annotated[BooksUseCase, Depends(get_books_uc)]) -> DomainBook:
    try:
        return await books_uc.get_current_book(book_uid=book_id)
    except BookNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
