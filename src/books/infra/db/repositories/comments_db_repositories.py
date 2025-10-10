import uuid

from sqlalchemy import delete, insert, select, update

from books.domain.entities.book_entities import DomainBook
from books.domain.entities.comment_entities import DomainComment
from books.domain.protocols.comments.db_protocols import CommentsDBProtocol
from books.infra.db.adapter.postgre_adapter import PostgresAdapter
from books.infra.db.models.comment_model import Comment as DBComment
from books.infra.mappers.comments_mappers import CommentsMapper


class CommentsDBRepository(CommentsDBProtocol):
    def __init__(self, db_adapter: PostgresAdapter):
        self.db_adapter = db_adapter

    async def get_comments(self, book: DomainBook) -> list[DomainComment]:
        query = select(DBComment).where(DBComment.book_uid == book.uid).order_by(DBComment.created_at.desc())
        async with self.db_adapter.get_session() as session:
            results = await session.scalars(query)
        return [CommentsMapper.orm_to_domain(comment) for comment in results]

    async def create_comment(self, comment: DomainComment, created_by: uuid.UUID, book_uid: uuid.UUID) -> DomainComment:
        query = (
            insert(DBComment)
            .values(text=comment.text, book_uid=book_uid, created_by=created_by)
            .returning(DBComment.uid, DBComment.text, DBComment.created_by, DBComment.created_at)
        )
        async with self.db_adapter.get_session() as session:
            result = await session.execute(query)
            await session.commit()
        return DomainComment(**result.mappings().first())

    async def get_books_comment_by_uid(self, book_uid: uuid.UUID, comment_uid: uuid.UUID) -> DomainComment | None:
        query = select(DBComment).where(DBComment.uid == comment_uid, DBComment.book_uid == book_uid)
        print(comment_uid, book_uid)
        async with self.db_adapter.get_session() as session:
            result = await session.execute(query)
        comment = result.scalar_one_or_none()
        if comment:
            return CommentsMapper.orm_to_domain(comment)
        return None

    async def update_comment(self, comment: DomainComment, update_data: dict, updated_by: uuid.UUID) -> None:
        query = update(DBComment).where(DBComment.uid == comment.uid).values(**update_data, updated_by=updated_by)
        async with self.db_adapter.get_session() as session:
            await session.execute(query)
            await session.commit()

    async def delete_comment(self, comment: DomainComment) -> None:
        query = delete(DBComment).where(DBComment.uid == comment.uid)
        async with self.db_adapter.get_session() as session:
            await session.execute(query)
            await session.commit()
