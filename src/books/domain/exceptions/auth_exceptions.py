from books.domain.exceptions.core_exceptions import CoreException


class AuthException(CoreException):
    pass

class AlreadyExistsException(AuthException):
    def __init__(self):
        super().__init__("User already exists.")

class WrongLoginDataException(AuthException):
    def __init__(self):
        super().__init__("Wrong username/email or password.")

class WrongSessionException(AuthException):
    def __init__(self):
        super().__init__("Current session is inactive or has been terminated.")

class TokenExpiredException(AuthException):
    def __init__(self):
        super().__init__("Token is expired.")

class InvalidTokenException(AuthException):
    def __init__(self):
        super().__init__("Token is invalid.")

class UserNotFoundException(AuthException):
    def __init__(self):
        super().__init__("Current user not found.")