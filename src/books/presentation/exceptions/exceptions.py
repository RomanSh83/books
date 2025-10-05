from fastapi import HTTPException
from starlette import status


class NotPermissionsException(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_403_FORBIDDEN, detail="You have not permission to perform this action.")
