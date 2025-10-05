import uuid
from dataclasses import dataclass

from books.domain.entities.author_entities import DomainAuthor


@dataclass(frozen=True)
class DomainBook:
    title: str
    author: DomainAuthor
    published_year: int
    description: str | None = None
    image: str | None = None
    uid: uuid.UUID | None = None
