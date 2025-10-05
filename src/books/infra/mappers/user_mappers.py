from books.domain.entities.user_entities import DomainUser
from books.infra.db.models.user_model import User as ORMUser


def orm_to_domain(user: ORMUser) -> DomainUser:
    return DomainUser(
        uid=user.uid,
        username=user.username,
        email=user.email,
        hashed_password=user.hashed_password,
        is_verified=user.is_verified,
        is_activated=user.is_activated,
        is_superuser=user.is_superuser,
    )
