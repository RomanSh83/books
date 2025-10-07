from typing import Annotated

from fastapi import Depends, Header, HTTPException
from starlette import status

from books.application.use_cases.auth_use_cases import AuthUseCase
from books.domain.entities.user_entities import DomainUser
from books.domain.exceptions.auth_exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    UserNotFoundException,
    WrongSessionException,
)
from books.infra.broker.adapter.redis_adapter import RedisAdapter, get_broker_adapter
from books.infra.broker.repositories.auth_broker_repositories import (
    AuthBrokerRepository,
)
from books.infra.db.adapter.postgre_adapter import PostgresAdapter, get_db_adapter
from books.infra.db.repositories.auth_db_repositories import AuthDBRepository
from books.infra.security.repositories.password_services import PasswordServiceService
from books.infra.security.repositories.token_service import TokenService


def get_auth_uc(
    db_adapter: Annotated[PostgresAdapter, Depends(get_db_adapter)],
    broker_adapter: Annotated[RedisAdapter, Depends(get_broker_adapter)],
):
    db = AuthDBRepository(db_adapter=db_adapter)
    broker = AuthBrokerRepository(broker_adapter=broker_adapter)
    password_service = PasswordServiceService()
    token_service = TokenService()

    return AuthUseCase(db=db, broker=broker, password_service=password_service, token_service=token_service)


def get_token(authorization_header: Annotated[str | None, Header(alias="Authorization")] = None) -> str:
    if not authorization_header:
        raise HTTPException(status_code=401, detail="The Authorization header is missing.")
    if not authorization_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="The Authorization header must be in the following format: Bearer <token>"
        )
    return authorization_header.replace("Bearer ", "")


async def get_current_user(
    auth_uc: Annotated[AuthUseCase, Depends(get_auth_uc)], token: Annotated[str, Depends(get_token)]
) -> DomainUser:
    try:
        return await auth_uc.get_current_user(token=token)
    except (WrongSessionException, TokenExpiredException, InvalidTokenException, UserNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
