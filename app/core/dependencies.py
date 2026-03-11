from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.modules.auth.utils import decode_token
from app.core.database import get_db
from app.modules.tenants.models import Tenant

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {
        "user_id": int(payload.get("sub")),
        "tenant_id": payload.get("tenant_id"),
        "role": payload.get("role")
    }

def get_current_tenant(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    tenant_id = current_user.get("tenant_id")

    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant not selected")

    tenant = (
        db.query(Tenant)
        .filter(Tenant.id == tenant_id)
        .first()
    )

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if not tenant.active:
        raise HTTPException(status_code=403, detail="Tenant inactive")

    return tenant