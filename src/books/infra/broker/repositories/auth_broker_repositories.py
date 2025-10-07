from uuid import UUID

from books.application.config import get_settings
from books.domain.protocols.auth.broker_protocols import AuthBrokerProtocol
from books.infra.broker.adapter.redis_adapter import RedisAdapter


class AuthBrokerRepository(AuthBrokerProtocol):
    def __init__(self, broker_adapter: RedisAdapter):
        self.broker_adapter = broker_adapter

    async def save_token(self, user_uid: UUID, token: str) -> None:
        async with self.broker_adapter.get_client() as client:
            await client.set(name=str(user_uid), value=token, ex=get_settings().TOKEN_EXPIRATION_MINUTES * 60)

    async def is_exists_token(self, user_uid: UUID, token: str) -> bool:
        async with self.broker_adapter.get_client() as client:
            return token == await client.get(name=str(user_uid))
