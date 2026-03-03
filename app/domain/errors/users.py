class UserAlreadyExistError(Exception):
  pass

class UserNotFoundError(Exception):
  pass

class InvalidCredentialsError(Exception):
  pass

class UserInactiveError(Exception):
  pass