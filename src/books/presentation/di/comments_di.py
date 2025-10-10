import uuid
from typing import Annotated

from fastapi import Depends, HTTPException
from starlette import status

from books.application.use_cases.comments_use_cases import CommentsUseCase
from books.domain.entities.comment_entities import DomainComment
from books.domain.exceptions.comments_exceptions import CommentNotFoundException
from books.infra.db.adapter.postgre_adapter import PostgresAdapter, get_db_adapter
from books.infra.db.repositories.comments_db_repositories import CommentsDBRepository


def get_comments_uc(
    db_adapter: Annotated[PostgresAdapter, Depends(get_db_adapter)],
):
    db = CommentsDBRepository(db_adapter=db_adapter)

    return CommentsUseCase(db=db)


async def get_current_comment(
    book_id: uuid.UUID, comment_id: uuid.UUID, comments_uc: Annotated[CommentsUseCase, Depends(get_comments_uc)]
) -> DomainComment:
    try:
        return await comments_uc.get_current_comment(book_uid=book_id, comment_uid=comment_id)

    except CommentNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
