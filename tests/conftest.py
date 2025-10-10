import datetime
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
from books.infra.db.models.author_model import Author as AuthorModel
from books.infra.db.models.book_model import Book as BookModel
from books.infra.db.models.comment_model import Comment as CommentModel
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


@pytest.fixture(scope="session")
def author():
    return {"first_name": "author_firstname", "last_name": "author_lastname", "birth_date": "1950-01-01"}


@pytest.fixture(scope="session")
def another_author():
    return {
        "first_name": "another_author_firstname",
        "last_name": "another_author_lastname",
        "birth_date": "1960-01-01",
    }


@pytest.fixture(scope="session")
def mutable_author():
    return {
        "first_name": "mutable_firstname",
        "last_name": "mutable_lastname",
        "birth_date": "1961-01-01",
    }


@pytest.fixture(scope="session")
def book(author_uid):
    return {
        "title": "book_title",
        "author_uid": str(author_uid),
        "published_year": 2000,
        "description": "book_description",
    }


@pytest.fixture(scope="session")
def another_book(another_author_uid):
    return {
        "title": "another_book_title",
        "author_uid": str(another_author_uid),
        "published_year": 2001,
        "description": "another_book_description",
    }


@pytest.fixture(scope="session")
def mutable_book(another_author_uid):
    return {
        "title": "mutable_book_title",
        "author_uid": str(another_author_uid),
        "published_year": 2002,
        "description": "mutable_book_description",
    }


@pytest.fixture(scope="session")
def comment(book_uid):
    return {
        "text": "comment",
        "book_uid": str(book_uid),
    }


@pytest.fixture(scope="session")
def another_comment(another_book_uid):
    return {
        "text": "another_comment",
        "book_uid": str(another_book_uid),
    }


@pytest.fixture(scope="session")
def mutable_comment(another_book_uid):
    return {
        "text": "mutable_comment",
        "book_uid": str(another_book_uid),
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
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")
    yield
    command.downgrade(alembic_config, "base")


@pytest_asyncio.fixture(scope="session", autouse=True)
async def registered_admin_user(prepare_pg_database, admin_user):
    query = (
        insert(UserModel)
        .values(
            username=admin_user["username"],
            email=admin_user["email"],
            hashed_password=get_hashed_password(password=admin_user["password"]),
            is_superuser=True,
        )
        .returning(UserModel.uid)
    )
    async with TestPostgresAdapter.get_session() as session:
        result = await session.scalar(query)
        await session.commit()
    return result


@pytest_asyncio.fixture(scope="session", autouse=True)
async def registered_regular_user(prepare_pg_database, regular_user):
    query = (
        insert(UserModel)
        .values(
            username=regular_user["username"],
            email=regular_user["email"],
            hashed_password=get_hashed_password(password=regular_user["password"]),
            is_superuser=False,
        )
        .returning(UserModel.uid)
    )

    async with TestPostgresAdapter.get_session() as session:
        result = await session.scalar(query)
        await session.commit()
    return result


@pytest_asyncio.fixture(scope="session", autouse=True)
async def registered_another_regular_user(prepare_pg_database, another_regular_user):
    query = (
        insert(UserModel)
        .values(
            username=another_regular_user["username"],
            email=another_regular_user["email"],
            hashed_password=get_hashed_password(password=another_regular_user["password"]),
            is_superuser=False,
        )
        .returning(UserModel.uid)
    )
    async with TestPostgresAdapter.get_session() as session:
        result = await session.scalar(query)
        await session.commit()
    return result


@pytest_asyncio.fixture(scope="session", autouse=True)
async def author_uid(prepare_pg_database, author, registered_admin_user):
    birth_date = author.pop("birth_date")
    query = (
        insert(AuthorModel)
        .values(
            **author, birth_date=datetime.datetime.strptime(birth_date, "%Y-%m-%d"), created_by=registered_admin_user
        )
        .returning(AuthorModel.uid)
    )
    async with TestPostgresAdapter.get_session() as session:
        author_uid = await session.scalar(query)
        await session.commit()
    return str(author_uid)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def another_author_uid(prepare_pg_database, another_author, registered_admin_user):
    birth_date = another_author.pop("birth_date")
    query = (
        insert(AuthorModel)
        .values(
            **another_author,
            birth_date=datetime.datetime.strptime(birth_date, "%Y-%m-%d"),
            created_by=registered_admin_user,
        )
        .returning(AuthorModel.uid)
    )
    async with TestPostgresAdapter.get_session() as session:
        author_uid = await session.scalar(query)
        await session.commit()
    return str(author_uid)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def mutable_author_uid(prepare_pg_database, mutable_author, registered_admin_user):
    birth_date = mutable_author.pop("birth_date")
    query = (
        insert(AuthorModel)
        .values(
            **mutable_author,
            birth_date=datetime.datetime.strptime(birth_date, "%Y-%m-%d"),
            created_by=registered_admin_user,
        )
        .returning(AuthorModel.uid)
    )
    async with TestPostgresAdapter.get_session() as session:
        author_uid = await session.scalar(query)
        await session.commit()
    return str(author_uid)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def book_uid(prepare_pg_database, book, registered_admin_user):
    query = insert(BookModel).values(**book, created_by=registered_admin_user).returning(BookModel.uid)
    async with TestPostgresAdapter.get_session() as session:
        book_uid = await session.scalar(query)
        await session.commit()
    return str(book_uid)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def another_book_uid(prepare_pg_database, another_book, registered_admin_user):
    query = insert(BookModel).values(**another_book, created_by=registered_admin_user).returning(BookModel.uid)
    async with TestPostgresAdapter.get_session() as session:
        book_uid = await session.scalar(query)
        await session.commit()
    return str(book_uid)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def mutable_book_uid(prepare_pg_database, mutable_book, registered_admin_user):
    query = insert(BookModel).values(**mutable_book, created_by=registered_admin_user).returning(BookModel.uid)
    async with TestPostgresAdapter.get_session() as session:
        book_uid = await session.scalar(query)
        await session.commit()
    return str(book_uid)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def comment_uid(prepare_pg_database, comment, registered_regular_user):
    query = insert(CommentModel).values(**comment, created_by=registered_regular_user).returning(CommentModel.uid)
    async with TestPostgresAdapter.get_session() as session:
        comment_uid = await session.scalar(query)
        await session.commit()
    return str(comment_uid)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def another_comment_uid(prepare_pg_database, another_comment, registered_regular_user):
    query = (
        insert(CommentModel).values(**another_comment, created_by=registered_regular_user).returning(CommentModel.uid)
    )
    async with TestPostgresAdapter.get_session() as session:
        comment_uid = await session.scalar(query)
        await session.commit()
    return str(comment_uid)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def mutable_comment_uid(prepare_pg_database, mutable_comment, registered_regular_user):
    query = (
        insert(CommentModel).values(**mutable_comment, created_by=registered_regular_user).returning(CommentModel.uid)
    )
    async with TestPostgresAdapter.get_session() as session:
        comment_uid = await session.scalar(query)
        await session.commit()
    return str(comment_uid)


# Test Client
@pytest_asyncio.fixture
async def test_client(app) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(base_url="http://test", transport=ASGITransport(app)) as client:
        yield client
