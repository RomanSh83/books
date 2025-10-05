import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DomainComment:
    text: str
    uid: uuid.UUID | None = None
    created_at: datetime | None = None
    created_by: uuid.UUID | None = None
