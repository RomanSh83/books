import tomllib
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from httpx import ASGITransport, AsyncClient
from passlib.context import CryptContext
from sqlalchemy import insert

from books.application.config import get_settings
from books.infra.db.models.user_model import User as UserModel
from books.presentation.routers import main_router
from tests.postgres_adapter_for_tests import get_test_db_adapter

TestPostgresAdapter = get_test_db_adapter()
test_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return test_ctx.hash(secret=password)


# Users Fixtures


@pytest.fixture(scope="session")
def admin_user():
    return {"username": "admin", "email": "admin@domain.com", "password": "admin_1A"}


@pytest.fixture(scope="session")
def regular_user():
    return {"username": "regular_user", "email": "regular_user@domain.com", "password": "regular_user_1A"}


@pytest.fixture(scope="session")
def another_regular_user():
    return {
        "username": "another_regular_user",
        "email": "another_regular_user@domain.com",
        "password": "another_regular_user_1A",
    }


# FastAPI App Fixtures
# ---------------------------------------------------------------------------------------------------------------------
@pytest.fixture
def app():
    app = FastAPI()
    app.mount(get_settings().MEDIA_URL, StaticFiles(directory=get_settings().MEDIA_ROOT), name="media")
    app.include_router(main_router)
    return app


# DB Fixtures
# ---------------------------------------------------------------------------------------------------------------------
# Migrate database at the beginning of a session and clean up upon exiting
@pytest.fixture(scope="session")
def prepare_pg_database():
    alembic_config = AlembicConfig("alembic.ini")
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        script_location = data["tool"]["alembic"]["script_location"]
    alembic_config.set_main_option("script_location", script_location)
    command.upgrade(alembic_config, "head")
    yield
    command.downgrade(alembic_config, "base")


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_admin_user(prepare_pg_database, admin_user):
    query = insert(UserModel).values(
        username=admin_user["username"],
        email=admin_user["email"],
        hashed_password=get_hashed_password(password=admin_user["password"]),
        is_superuser=True,
    )
    async with TestPostgresAdapter.get_session() as session:
        await session.execute(query)
        await session.commit()


# Test Client
@pytest_asyncio.fixture
async def test_client(app) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(base_url="http://test", transport=ASGITransport(app)) as client:
        yield client
