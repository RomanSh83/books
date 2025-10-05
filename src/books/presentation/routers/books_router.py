from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from books.application.use_cases.books_use_cases import BooksUseCase
from books.domain.entities.book_entities import DomainBook
from books.domain.entities.user_entities import DomainUser
from books.domain.exceptions.authors_exceptions import AuthorNotFoundException
from books.domain.exceptions.books_exceptions import TitleAuthorConstraintException
from books.presentation.di.auth_di import get_current_user
from books.presentation.di.books_di import get_books_uc, get_current_book
from books.presentation.permissions.permissions import check_permissions_is_admin
from books.presentation.routers.comments_router import comments_router
from books.presentation.schemas.books_schemas import (
    BookReturnSchema,
    BooksFilterAndPaginationMixin,
    BooksInSchema,
    BooksPaginatedReturnSchema,
    BookUpdateSchema,
)

books_router = APIRouter(prefix="/books", tags=["books"])
books_router.include_router(comments_router, prefix="/comments", tags=["comments"])


@books_router.get(path="", status_code=status.HTTP_200_OK)
async def get_books(
    params: Annotated[BooksFilterAndPaginationMixin, Query()], books_uc: Annotated[BooksUseCase, Depends(get_books_uc)]
) -> BooksPaginatedReturnSchema:
    total, books = await books_uc.get_books(params=params.model_dump())
    return BooksPaginatedReturnSchema(books=books, total=total, limit=params.limit, offset=params.offset)


@books_router.get(path="/{book_id}", response_model=BookReturnSchema, status_code=status.HTTP_200_OK)
async def get_book(book: Annotated[DomainBook, Depends(get_current_book)]):
    return book


@books_router.post(path="", response_model=BookReturnSchema, status_code=status.HTTP_201_CREATED)
async def create_book(
    _: Annotated[Any, Depends(check_permissions_is_admin)],
    user: Annotated[DomainUser, Depends(get_current_user)],
    book_data: BooksInSchema,
    books_uc: Annotated[BooksUseCase, Depends(get_books_uc)],
):
    try:
        return await books_uc.create_book(user=user, book_data=book_data)
    except TitleAuthorConstraintException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except AuthorNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))


@books_router.put(path="/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(
    _: Annotated[Any, Depends(check_permissions_is_admin)],
    update_data: BookUpdateSchema,
    user: Annotated[DomainUser, Depends(get_current_user)],
    book: Annotated[DomainBook, Depends(get_current_book)],
    books_uc: Annotated[BooksUseCase, Depends(get_books_uc)],
):
    try:
        await books_uc.update_book(user=user, book=book, update_data=update_data.model_dump(exclude_unset=True))
    except TitleAuthorConstraintException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@books_router.delete(path="/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    _: Annotated[Any, Depends(check_permissions_is_admin)],
    book: Annotated[DomainBook, Depends(get_current_book)],
    books_uc: Annotated[BooksUseCase, Depends(get_books_uc)],
):
    await books_uc.delete_book(book=book)
