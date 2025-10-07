import uuid
from typing import Protocol

from books.domain.entities.user_entities import DomainUser


class AuthDBProtocol(Protocol):
    async def create_user(self, user: DomainUser) -> DomainUser:
        raise NotImplementedError

    async def get_user_by_login_field(self, username: str | None, email: str | None) -> DomainUser | None:
        raise NotImplementedError

    async def get_user_by_uid(self, user_uid: uuid.UUID) -> DomainUser | None:
        raise NotImplementedError
