import uuid

from books.domain.entities.user_entities import DomainUser
from books.domain.exceptions.auth_exceptions import WrongLoginDataException, WrongSessionException, UserNotFoundException
from books.domain.protocols.auth.broker_protocols import AuthBrokerProtocol
from books.domain.protocols.auth.db_protocols import AuthDBProtocol
from books.domain.protocols.auth.password_protocols import PasswordServiceProtocol
from books.domain.protocols.auth.token_protocols import TokenServiceProtocol
from books.presentation.schemas.auth_schemas import UserRegisterInSchema, TokenSchema, UserInSchema


class AuthUseCase:
    def __init__(
        self,
        db: AuthDBProtocol,
        broker: AuthBrokerProtocol,
        password_service: PasswordServiceProtocol,
        token_service: TokenServiceProtocol
    ):
        self.db = db
        self.broker = broker
        self.password_service = password_service
        self.token_service = token_service

    async def register_user(self, user_data: UserRegisterInSchema) -> DomainUser:
        hashed_password = await self.password_service.hash_password(password=user_data.password)
        domain_user = DomainUser(username=user_data.username, email=user_data.email, hashed_password=hashed_password)
        return await self.db.create_user(user=domain_user)

    async def login_user(self, user_data: UserInSchema) -> TokenSchema:
        domain_user = await self.db.get_user_by_login_field(username=user_data.username, email=user_data.email)
        if (
            not domain_user
            or not await self.password_service.verify_password(user_data.password, domain_user.hashed_password)
        ):
            raise WrongLoginDataException
        token = self.token_service.get_token(domain_user)
        await self.broker.save_token(user_uid=domain_user.uid, token=token)
        return TokenSchema(token=token)

    async def get_current_user(self, token: str) -> DomainUser:
        token_payload = self.token_service.decode_token(token=token)
        user_uid = uuid.UUID(token_payload["user_uid"])
        if not await self.broker.is_exists_token(user_uid=user_uid, token=token):
            raise WrongSessionException
        current_user = await self.db.get_user_by_uid(user_uid=user_uid)
        if not current_user:
            raise UserNotFoundException
        return current_user

