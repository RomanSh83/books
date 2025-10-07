from typing import Protocol


class PasswordServiceProtocol(Protocol):
    async def hash_password(self, password: str) -> str:
        raise NotImplementedError

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        raise NotImplementedError
