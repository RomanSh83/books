from datetime import UTC, datetime, timedelta

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from books.application.config import get_settings
from books.domain.entities.user_entities import DomainUser
from books.domain.exceptions.auth_exceptions import (
    InvalidTokenException,
    TokenExpiredException,
)
from books.domain.protocols.auth.token_protocols import TokenServiceProtocol


class TokenService(TokenServiceProtocol):
    @staticmethod
    def get_token(user: DomainUser) -> str:
        payload = {
            "user_uid": str(user.uid),
            "exp": datetime.now(UTC) + timedelta(minutes=get_settings().TOKEN_EXPIRATION_MINUTES),
        }
        return jwt.encode(payload=payload, key=get_settings().SECRET_KEY, algorithm="HS256")

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            jwt.decode(token, key=get_settings().SECRET_KEY, algorithms=["HS256"])
        except ExpiredSignatureError:
            raise TokenExpiredException
        except InvalidTokenError:
            raise InvalidTokenException
        payload = jwt.decode(token, key=get_settings().SECRET_KEY, algorithms=["HS256"])
        if "user_uid" not in payload:
            raise InvalidTokenException
        return payload
