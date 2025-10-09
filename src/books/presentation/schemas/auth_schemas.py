import uuid
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, model_validator

from books.application.config import get_settings
from books.presentation.schemas.mixins.auth_mixins_schemas import (
    PasswordRegexValidationMixin,
)


class UserBaseSchema(BaseModel):
    username: Annotated[str, Field(min_length=get_settings().AUTH_USERNAME_MIN_LENGTH)]
    email: EmailStr


class UserRegisterInSchema(PasswordRegexValidationMixin, UserBaseSchema):
    model_config = {"extra": "forbid"}
    password: str


class UserReturnSchema(UserBaseSchema):
    uid: uuid.UUID
    is_verified: bool
    is_activated: bool
    is_superuser: bool


class UserInSchema(PasswordRegexValidationMixin, BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str

    @model_validator(mode="after")
    def username_or_email_field_required(cls, model_instance):
        if all(getattr(model_instance, field) is None for field in ["username", "email"]):
            raise ValueError("At least one field_required.")
        return model_instance


class TokenSchema(BaseModel):
    token: str
