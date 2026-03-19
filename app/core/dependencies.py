from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.modules.auth.utils import decode_token
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    return {
        "user_id": int(payload.get("sub")),
        "tenant_id": payload.get("tenant_id"),
        "role": payload.get("role")
    }