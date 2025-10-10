from typing import Annotated

from fastapi import Depends

from books.domain.entities.comment_entities import DomainComment
from books.domain.entities.user_entities import DomainUser
from books.presentation.di.auth_di import get_current_user
from books.presentation.di.comments_di import get_current_comment
from books.presentation.exceptions.exceptions import NotPermissionsException


def check_permissions_is_admin(user: Annotated[DomainUser, Depends(get_current_user)]):
    if not user.is_superuser:
        raise NotPermissionsException


def check_permissions_comment_is_author_or_admin(
    user: Annotated[DomainUser, Depends(get_current_user)],
    comment: Annotated[DomainComment, Depends(get_current_comment)],
):
    if not (user.is_superuser or comment.created_by == user.uid):
        raise NotPermissionsException
