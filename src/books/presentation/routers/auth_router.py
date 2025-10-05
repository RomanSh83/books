from json import JSONDecoder, JSONEncoder
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Header
from starlette import status

from books.application.use_cases.auth_use_cases import AuthUseCase
from books.domain.entities.user_entities import DomainUser
from books.domain.exceptions.auth_exceptions import AlreadyExistsException, WrongLoginDataException
from books.presentation.di.auth_di import get_auth_uc, get_token, get_current_user
from books.presentation.schemas.auth_schemas import UserReturnSchema, UserRegisterInSchema, UserInSchema, TokenSchema

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post(
    path="/register",
    response_model=UserReturnSchema,
    status_code=status.HTTP_201_CREATED
)
async def register_user(
    user: UserRegisterInSchema,
    auth_uc: Annotated[AuthUseCase, Depends(get_auth_uc)],
):
    try:
        return await auth_uc.register_user(user)
    except AlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@auth_router.post(
    path="/login",
    response_model=TokenSchema,
    status_code=status.HTTP_200_OK
)
async def login_user(
    user: UserInSchema,
    auth_uc: Annotated[AuthUseCase, Depends(get_auth_uc)],
):
    try:
        return await auth_uc.login_user(user)
    except WrongLoginDataException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@auth_router.get(
    path="/me",
    response_model=UserReturnSchema,
    status_code=status.HTTP_200_OK
)
async def get_user(user: Annotated[DomainUser, Depends(get_current_user)]):
    return user
