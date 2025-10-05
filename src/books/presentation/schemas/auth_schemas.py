import re
import uuid

from pydantic import BaseModel, EmailStr, field_validator

from books.application.config import get_settings

class UserBaseSchema(BaseModel):
    username: str
    email: EmailStr


class UserRegisterInSchema(UserBaseSchema):
    password: str

    @field_validator("password")
    def validate_password_regex(cls, value: str) -> str:
        min_length = get_settings().PASSWORD_MIN_LENGTH
        max_length = get_settings().PASSWORD_MAX_LENGTH
        match_conditions = r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[`\-~!@#$%^&*()=_+\[\]{};:'\"\\|<>/?№.,])"
        allowed_characters = r"[\w`\-~!@#$%^&*()=+\[\]{};:'\"\\|<>/?№.,]"
        length_conditions = "{" + str(min_length) + "," + str(max_length) + "}"
        if not re.fullmatch(pattern=f"^{match_conditions}{allowed_characters}{length_conditions}$", string=value):
            raise ValueError(
                f"Password must be between {min_length} and {max_length} characters long and meet complexity requirements."
            )
        return value

class UserReturnSchema(UserBaseSchema):
    uid: uuid.UUID
    is_verified: bool
    is_activated: bool
    is_superuser: bool

class UserInSchema(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str

class TokenSchema(BaseModel):
    token: str