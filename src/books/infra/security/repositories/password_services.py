from passlib.context import CryptContext

from books.application.base.singleton import Singleton
from books.domain.protocols.auth.password_protocols import PasswordServiceProtocol


class PasswordServiceService(PasswordServiceProtocol, Singleton):
    ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def hash_password(self, password: str) -> str:
        return self.ctx.hash(secret=password)

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.ctx.verify(password, hashed_password)
