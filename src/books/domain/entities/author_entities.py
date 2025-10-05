import uuid
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DomainAuthor:
    first_name: str
    last_name: str
    birth_date: date
    bio: str | None = None
    uid: uuid.UUID | None = None
