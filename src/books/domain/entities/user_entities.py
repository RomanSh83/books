import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class DomainUser:
    username: str
    email: str
    hashed_password: str
    uid: uuid.UUID | None = None
    is_activated: bool | None = True # for future purposes
    is_verified: bool | None = True # for future purposes
    is_superuser: bool | None = False
