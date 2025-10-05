from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from books.application.use_cases.authors_use_cases import AuthorsUseCase
from books.domain.entities.author_entities import DomainAuthor
from books.domain.entities.user_entities import DomainUser
from books.domain.exceptions.authors_exceptions import (
    FirstLastNameBirthDateConstraintException,
)
from books.presentation.di.auth_di import get_current_user
from books.presentation.di.authors_di import get_authors_uc, get_current_author
from books.presentation.permissions.permissions import check_permissions_is_admin
from books.presentation.schemas.authors_shemas import (
    AuthorInSchema,
    AuthorReturnSchema,
    AuthorUpdateSchema,
)

authors_router = APIRouter(prefix="/authors", tags=["authors"])


@authors_router.get(path="", response_model=list[AuthorReturnSchema], status_code=status.HTTP_200_OK)
async def get_authors(
    authors_uc: Annotated[AuthorsUseCase, Depends(get_authors_uc)],
):
    return await authors_uc.get_authors()


@authors_router.get(path="/{author_id}", response_model=AuthorReturnSchema, status_code=status.HTTP_200_OK)
async def get_author(author: Annotated[DomainAuthor, Depends(get_current_author)]):
    return author


@authors_router.post(path="", response_model=AuthorReturnSchema, status_code=status.HTTP_201_CREATED)
async def create_author(
    _: Annotated[Any, Depends(check_permissions_is_admin)],
    user: Annotated[DomainUser, Depends(get_current_user)],
    author_data: AuthorInSchema,
    authors_uc: Annotated[AuthorsUseCase, Depends(get_authors_uc)],
):
    try:
        return await authors_uc.create_author(user=user, author_data=author_data)
    except FirstLastNameBirthDateConstraintException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@authors_router.put(path="/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_author(
    _: Annotated[Any, Depends(check_permissions_is_admin)],
    update_data: AuthorUpdateSchema,
    user: Annotated[DomainUser, Depends(get_current_user)],
    author: Annotated[DomainAuthor, Depends(get_current_author)],
    authors_uc: Annotated[AuthorsUseCase, Depends(get_authors_uc)],
):
    try:
        await authors_uc.update_author(user=user, author=author, update_data=update_data.model_dump(exclude_unset=True))
    except FirstLastNameBirthDateConstraintException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@authors_router.delete(path="/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
    _: Annotated[Any, Depends(check_permissions_is_admin)],
    author: Annotated[DomainAuthor, Depends(get_current_author)],
    authors_uc: Annotated[AuthorsUseCase, Depends(get_authors_uc)],
):
    await authors_uc.delete_author(author=author)
