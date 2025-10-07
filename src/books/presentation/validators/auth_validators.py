import re

from books.application.config import get_settings


def validate_password_regex(value: str) -> str:
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
