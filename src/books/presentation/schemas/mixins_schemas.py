from typing import Annotated

from pydantic import Field, model_validator

from books.application.config import get_settings
from books.presentation.validators.base_validators import (
    at_least_one_field_required_validator,
)


class AtLeastOneFieldMixin:
    @model_validator(mode="after")
    def at_least_one_field_required(cls, model_instance):
        return at_least_one_field_required_validator(instance=model_instance)


class PaginationOffsetLimitMixin:
    limit: Annotated[int, Field(gt=0, le=get_settings().PAGINATION_MAX_LIMIT)] = get_settings().PAGINATION_DEFAULT_LIMIT
    offset: Annotated[int, Field(ge=0, le=50)] = 0
