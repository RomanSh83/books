class CoreException(Exception):
    pass


class Base64DecodeError(CoreException):
    def __init__(self):
        super().__init__("Invalid base64 data.")
