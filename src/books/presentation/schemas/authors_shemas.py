import uuid
from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field

from books.application.config import get_settings
from books.presentation.schemas.mixins.base_mixins_schemas import AtLeastOneFieldMixin

_name_field = Field(min_length=get_settings().AUTHOR_NAME_MIN_LENGTH, max_length=get_settings().AUTHOR_NAME_MAX_LENGTH)
_birth_date_field = Field(lt=date.today().replace(year=date.today().year - get_settings().AUTHOR_MIN_AUTHOR_AGE))


class AuthorBaseSchema(BaseModel):
    first_name: Annotated[str, _name_field]
    last_name: Annotated[str, _name_field]
    birth_date: Annotated[date, _birth_date_field]
    bio: str | None = None


class AuthorInSchema(AuthorBaseSchema):
    pass


class AuthorReturnSchema(AuthorBaseSchema):
    uid: uuid.UUID


class AuthorUpdateSchema(AtLeastOneFieldMixin, BaseModel):
    first_name: Annotated[str | None, _name_field] = None
    last_name: Annotated[str | None, _name_field] = None
    birth_date: Annotated[date | None, _birth_date_field] = None
    bio: str | None = None
