import uuid
from dataclasses import asdict

from sqlalchemy import insert, select, and_
from sqlalchemy.exc import IntegrityError

from books.domain.entities.user_entities import DomainUser
from books.domain.exceptions.auth_exceptions import AlreadyExistsException
from books.domain.protocols.auth.db_protocols import AuthDBProtocol
from books.infra.db.adapter.postgre_adapter import PostgresAdapter
from books.infra.db.models.user_model import User as DBUser
from books.infra.mappers.user_mappers import orm_to_domain


class AuthDBRepository(AuthDBProtocol):
    def __init__(self, db_adapter: PostgresAdapter):
        self.db_adapter = db_adapter

    async def create_user(self, user: DomainUser) -> DomainUser:
        user_data = asdict(user)
        user_data.pop("uid")
        query = insert(
            DBUser
        ).values(
            **user_data
        ).returning(
            DBUser.uid, DBUser.username, DBUser.email, DBUser.hashed_password, DBUser.is_verified, DBUser.is_superuser, DBUser.is_activated
        )
        async with self.db_adapter.get_session() as session:
            try:
                result = await session.execute(query)
                await session.commit()
            except IntegrityError as e:
                await session.rollback()
                raise AlreadyExistsException()
        return DomainUser(**result.mappings().first())

    async def _get_user_by_fields(self, conditions: list) -> DomainUser | None:
        query = select(DBUser).where(and_(*conditions))
        async with self.db_adapter.get_session() as session:
            result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user:
            return orm_to_domain(user=user)
        return None

    async def get_user_by_login_field(self, username: str | None, email: str | None) -> DomainUser | None:
        conditions = []
        if username:
            conditions.append(DBUser.username == username)
        if email:
            conditions.append(DBUser.email == email)
        return await self._get_user_by_fields(conditions=conditions)

    async def get_user_by_uid(self, user_uid: uuid.UUID) -> DomainUser | None:
        return await self._get_user_by_fields(conditions=[DBUser.uid == user_uid])

def get_pg_auth_repository():
    return AuthDBRepository(db_adapter=PostgresAdapter())