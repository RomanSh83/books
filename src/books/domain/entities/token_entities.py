from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DomainToken:
    user_uid: str
    exp: datetime