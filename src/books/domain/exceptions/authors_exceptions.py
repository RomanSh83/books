from books.domain.exceptions.core_exceptions import CoreException


class AuthorsException(CoreException):
    pass


class FirstLastNameBirthDateConstraintException(AuthorsException):
    def __init__(self):
        super().__init__("Author already exists.")


class AuthorNotFoundException(AuthorsException):
    def __init__(self):
        super().__init__("Author not found.")
