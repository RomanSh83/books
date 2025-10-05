from books.domain.exceptions.core_exceptions import CoreException


class CommentsException(CoreException):
    pass


class CommentNotFoundException(CommentsException):
    def __init__(self):
        super().__init__("Comment not found.")
