from fastapi import HTTPException, status


class UserAlreadyExistError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class InvalidCredentialsError(Exception):
    pass

class UserInactiveError(Exception):
    pass

class InsufficientPermissionsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Insufficient permissions'
        )
