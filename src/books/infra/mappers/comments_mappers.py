from books.domain.entities.comment_entities import DomainComment
from books.infra.db.models.comment_model import Comment as ORMComment


class CommentsMapper:
    @staticmethod
    def orm_to_domain(comment: ORMComment) -> DomainComment:
        return DomainComment(
            uid=comment.uid, text=comment.text, created_by=comment.created_by, created_at=comment.created_at
        )
