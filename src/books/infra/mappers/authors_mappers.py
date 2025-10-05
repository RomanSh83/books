from books.domain.entities.author_entities import DomainAuthor
from books.infra.db.models.author_model import Author as ORMAuthor


class AuthorsMapper:
    @staticmethod
    def orm_to_domain(author: ORMAuthor) -> DomainAuthor:
        return DomainAuthor(
            uid=author.uid,
            first_name=author.first_name,
            last_name=author.last_name,
            birth_date=author.birth_date,
            bio=author.bio,
        )
