from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.settings import settings

def create_access_token(data: dict, expires_delta: int = 60 * 4):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt

def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )

        return payload

    except JWTError:
        return None