import uuid

from books.domain.entities.book_entities import DomainBook
from books.domain.entities.comment_entities import DomainComment
from books.domain.entities.user_entities import DomainUser
from books.domain.exceptions.comments_exceptions import CommentNotFoundException
from books.domain.protocols.comments.db_protocols import CommentsDBProtocol
from books.presentation.schemas.comments_schemas import CommentsInSchema


class CommentsUseCase:
    def __init__(self, db: CommentsDBProtocol):
        self.db = db

    async def get_comments(self, book: DomainBook) -> list[DomainComment]:
        return await self.db.get_comments(book=book)

    async def create_comment(self, user: DomainUser, book: DomainBook, comment_data: CommentsInSchema) -> DomainComment:
        domain_comment = DomainComment(**comment_data.model_dump())
        return await self.db.create_comment(comment=domain_comment, created_by=user.uid, book_uid=book.uid)

    async def get_current_comment(self, comment_uid: uuid.UUID) -> DomainComment:
        current_comment = await self.db.get_comment_by_uid(comment_uid=comment_uid)
        if not current_comment:
            raise CommentNotFoundException
        return current_comment

    async def update_comment(self, user: DomainUser, comment: DomainComment, update_data: dict) -> None:
        await self.db.update_comment(comment=comment, update_data=update_data, updated_by=user.uid)

    async def delete_comment(self, comment: DomainComment) -> None:
        await self.db.delete_comment(comment=comment)
