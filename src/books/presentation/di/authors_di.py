import uuid
from typing import Annotated

from fastapi import Depends, HTTPException
from starlette import status

from books.application.use_cases.authors_use_cases import AuthorsUseCase
from books.domain.entities.author_entities import DomainAuthor
from books.domain.exceptions.authors_exceptions import AuthorNotFoundException
from books.infra.db.adapter.postgre_adapter import PostgresAdapter, get_db_adapter
from books.infra.db.repositories.authors_db_repositories import AuthorsDBRepository


def get_authors_uc(
    db_adapter: Annotated[PostgresAdapter, Depends(get_db_adapter)],
):
    db = AuthorsDBRepository(db_adapter=db_adapter)

    return AuthorsUseCase(db=db)


async def get_current_author(
    author_id: uuid.UUID,
    author_uc: Annotated[AuthorsUseCase, Depends(get_authors_uc)],
) -> DomainAuthor:
    try:
        return await author_uc.get_current_author(author_uid=author_id)
    except AuthorNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
