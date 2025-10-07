from pydantic import field_validator

from books.presentation.validators.auth_validators import validate_password_regex


class PasswordRegexValidationMixin:
    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        return validate_password_regex(value=value)
