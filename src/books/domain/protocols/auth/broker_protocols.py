from typing import Protocol
from uuid import UUID


class AuthBrokerProtocol(Protocol):
    async def save_token(self, user_uid: UUID, token: str) -> None:
        raise NotImplementedError()

    async def is_exists_token(self, user_uid: UUID, token: str) -> bool:
        raise NotImplementedError()
