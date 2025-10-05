from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from books.application.base.singleton import Singleton
from books.application.config import get_settings


class PostgresAdapter(Singleton):
    def __init__(self) -> None:
        self._engine = create_async_engine(url=get_settings().DATABASE_URL)
        self._session_factory = async_sessionmaker(bind=self._engine, expire_on_commit=False, autocommit=False)

    @property
    def get_session(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory

def get_db_adapter() -> PostgresAdapter:
    return PostgresAdapter()