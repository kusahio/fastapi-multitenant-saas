from datetime import datetime, timedelta
from jose import jwt
from app.core.settings import settings

def create_access_token(data: dict, expires_delta: int = 60 * 4):
  to_encode = data.copy()

  expire = datetime.now(datetime.timezone.utc) + timedelta(minutes=expires_delta)

  to_encode.update({'exp': expire})

  encoded_jwt = jwt.encode(
    to_encode,
    settings.jwt_secret,
    algorithm=settings.jwt_algorithm
  )

  return encoded_jwt