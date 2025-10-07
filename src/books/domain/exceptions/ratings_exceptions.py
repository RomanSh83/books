from books.domain.exceptions.core_exceptions import CoreException


class RatingsException(CoreException):
    pass


class BookNotRatedException(RatingsException):
    def __init__(self):
        super().__init__("This book does not have a rating.")


class BookAlreadyRatedException(RatingsException):
    def __init__(self):
        super().__init__("You have already rated this book.")
