from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from books.application.use_cases.ratings_use_cases import RatingsUseCase
from books.domain.entities.book_entities import DomainBook
from books.domain.entities.user_entities import DomainUser
from books.presentation.di.auth_di import get_current_user
from books.presentation.di.books_di import get_current_book
from books.presentation.di.ratings_di import get_ratings_uc
from books.presentation.schemas.ratings_schemas import RatingReturnSchema

rating_router = APIRouter(prefix="/rating", tags=["rating"])


@rating_router.post(path="", status_code=status.HTTP_201_CREATED)
async def rate_book(
    user: Annotated[DomainUser, Depends(get_current_user)],
    book: Annotated[DomainBook, Depends(get_current_book)],
    points: int,
    ratings_uc: Annotated[RatingsUseCase, Depends(get_ratings_uc)],
):
    await ratings_uc.rate_book(user=user, book=book, points=points)


@rating_router.get(path="", response_model=RatingReturnSchema, status_code=status.HTTP_200_OK)
async def get_comments(
    rating: Annotated[RatingReturnSchema, Depends(get_ratings_uc)],
):
    return rating
