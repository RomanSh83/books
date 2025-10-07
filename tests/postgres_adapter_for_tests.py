"""
Тестовый PostgresAdapter.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from books.application.config import get_settings


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


class PostgresAdapter(Singleton):
    def __init__(self) -> None:
        self._engine = create_async_engine(url=get_settings().DATABASE_URL)
        self._session_factory = async_sessionmaker(bind=self._engine, expire_on_commit=False, autocommit=False)

    @property
    def get_session(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory


def get_test_db_adapter() -> PostgresAdapter:
    return PostgresAdapter()
