import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from books.application.config import get_settings


class CommentsBaseSchema(BaseModel):
    text: Annotated[
        str, Field(min_length=get_settings().COMMENT_TEXT_MIN_LENGTH, max_length=get_settings().COMMENT_TEXT_MAX_LENGTH)
    ]


class CommentsInSchema(CommentsBaseSchema):
    model_config = {"extra": "forbid"}
    pass


class CommentReturnSchema(CommentsBaseSchema):
    uid: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime


class CommentUpdateSchema(CommentsBaseSchema):
    pass
