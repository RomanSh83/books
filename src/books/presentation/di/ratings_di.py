from typing import Annotated

from fastapi import Depends, HTTPException
from starlette import status

from books.application.use_cases.ratings_use_cases import RatingsUseCase
from books.domain.entities.book_entities import DomainBook
from books.domain.exceptions.books_exceptions import BookNotFoundException
from books.infra.db.adapter.postgre_adapter import PostgresAdapter, get_db_adapter
from books.infra.db.repositories.ratings_db_repositories import RatingsDBRepository
from books.presentation.di.books_di import get_current_book
from books.presentation.schemas.ratings_schemas import RatingReturnSchema


def get_ratings_uc(
    db_adapter: Annotated[PostgresAdapter, Depends(get_db_adapter)],
):
    db = RatingsDBRepository(db_adapter=db_adapter)

    return RatingsUseCase(db=db)


async def get_current_rating(
    book: Annotated[DomainBook, Depends(get_current_book)],
    ratings_uc: Annotated[RatingsUseCase, Depends(get_ratings_uc)],
) -> RatingReturnSchema:
    try:
        return await ratings_uc.get_rating(book=book)
    except BookNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
