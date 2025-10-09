import uuid
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from books.application.config import get_settings
from books.domain.entities.author_entities import DomainAuthor
from books.presentation.schemas.mixins.base_mixins_schemas import (
    AtLeastOneFieldMixin,
    PaginationOffsetLimitMixin,
)
from books.presentation.validators.books_validators import image_base64_field_validator

_title_field = Field(min_length=get_settings().BOOK_TITLE_MIN_LENGTH, max_length=get_settings().BOOK_TITLE_MAX_LENGTH)
_published_year_field = Field(ge=get_settings().BOOK_MIN_PUBLISHED_YEAR, le=get_settings().BOOK_MAX_PUBLISHED_YEAR)


class BooksBaseSchema(BaseModel):
    title: Annotated[str, _title_field]
    published_year: Annotated[int, _published_year_field]
    description: str


class BooksImageUriSchema:
    image_uri: Annotated[str | None, Field(alias="image")] = None

    @field_validator("image_uri", mode="after")
    def validate_image(cls, value):
        return image_base64_field_validator(value)


class BooksInSchema(BooksBaseSchema, BooksImageUriSchema):
    model_config = {"extra": "forbid"}
    author: uuid.UUID


class BookReturnSchema(BooksBaseSchema):
    uid: uuid.UUID
    author: DomainAuthor
    image: str | None


class BooksFilterSchema(BaseModel):
    title: str | None = None
    author: str | uuid.UUID | None = None


class BooksFilterAndPaginationMixin(PaginationOffsetLimitMixin, BooksFilterSchema):
    pass


class BooksPaginatedReturnSchema(BaseModel):
    books: list[BookReturnSchema]
    total: int
    limit: int
    offset: int


class BookUpdateSchema(AtLeastOneFieldMixin, BooksImageUriSchema, BaseModel):
    title: Annotated[str | None, _title_field] = None
    author_uid: Annotated[uuid.UUID | None, Field(alias="author")] = None
    published_year: Annotated[int | None, _published_year_field] = None
    description: str | None = None
