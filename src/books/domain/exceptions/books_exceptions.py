from books.domain.exceptions.core_exceptions import CoreException


class BooksException(CoreException):
    pass


class TitleAuthorConstraintException(BooksException):
    def __init__(self):
        super().__init__("Book already exists.")


class BookNotFoundException(BooksException):
    def __init__(self):
        super().__init__("Book not found.")
