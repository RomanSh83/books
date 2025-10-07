from contextlib import asynccontextmanager

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from books.application.base.singleton import Singleton
from books.application.config import get_settings


class RedisAdapter(Singleton):
    def __init__(self):
        self.connection_pool = ConnectionPool.from_url(
            url=get_settings().REDIS_URL,
            max_connections=get_settings().REDIS_MAX_CONNECTIONS,
            decode_responses=True,
            encoding="utf-8",
        )

    @asynccontextmanager
    async def get_client(self):
        client = redis.Redis(connection_pool=self.connection_pool)
        try:
            yield client
        finally:
            await client.aclose()


def get_broker_adapter() -> RedisAdapter:
    return RedisAdapter()
