from typing import Annotated, Any

from fastapi import APIRouter, Depends
from starlette import status

from books.application.use_cases.comments_use_cases import CommentsUseCase
from books.domain.entities.book_entities import DomainBook
from books.domain.entities.comment_entities import DomainComment
from books.domain.entities.user_entities import DomainUser
from books.presentation.di.auth_di import get_current_user
from books.presentation.di.books_di import get_current_book
from books.presentation.di.comments_di import get_comments_uc, get_current_comment
from books.presentation.permissions.permissions import (
    check_permissions_comment_is_author_or_admin,
)
from books.presentation.schemas.comments_schemas import (
    CommentReturnSchema,
    CommentsInSchema,
    CommentUpdateSchema,
)

comments_router = APIRouter(prefix="/comments", tags=["comments"])


@comments_router.get(path="", response_model=list[CommentReturnSchema], status_code=status.HTTP_200_OK)
async def get_comments(
    book: Annotated[DomainBook, Depends(get_current_book)],
    comments_uc: Annotated[CommentsUseCase, Depends(get_comments_uc)],
):
    return await comments_uc.get_comments(book=book)


@comments_router.get(path="/{comment_id}", response_model=CommentReturnSchema, status_code=status.HTTP_200_OK)
async def get_comment(comment: Annotated[DomainComment, Depends(get_current_comment)]):
    return comment


@comments_router.post(path="", response_model=CommentReturnSchema, status_code=status.HTTP_201_CREATED)
async def create_comment(
    user: Annotated[DomainUser, Depends(get_current_user)],
    book: Annotated[DomainBook, Depends(get_current_book)],
    comment_data: CommentsInSchema,
    comments_uc: Annotated[CommentsUseCase, Depends(get_comments_uc)],
):
    return await comments_uc.create_comment(user=user, book=book, comment_data=comment_data)


@comments_router.put(path="/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_comment(
    _: Annotated[Any, Depends(check_permissions_comment_is_author_or_admin)],
    user: Annotated[DomainUser, Depends(get_current_user)],
    update_data: CommentUpdateSchema,
    comment: Annotated[DomainComment, Depends(get_current_comment)],
    comments_uc: Annotated[CommentsUseCase, Depends(get_comments_uc)],
):
    await comments_uc.update_comment(user=user, comment=comment, update_data=update_data.model_dump(exclude_unset=True))


@comments_router.delete(path="/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    _: Annotated[Any, Depends(check_permissions_comment_is_author_or_admin)],
    comment: Annotated[DomainComment, Depends(get_current_comment)],
    comments_uc: Annotated[CommentsUseCase, Depends(get_comments_uc)],
):
    await comments_uc.delete_comment(comment=comment)
