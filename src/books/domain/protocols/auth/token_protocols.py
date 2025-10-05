from typing import Protocol

from books.domain.entities.user_entities import DomainUser


class TokenServiceProtocol(Protocol):
    @staticmethod
    def get_token(user: DomainUser) -> str:
        raise NotImplementedError()

    @staticmethod
    def decode_token(token: str) -> dict:
        raise NotImplementedError()