from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.limiter import limiter
from app.modules.auth.service import AuthService
from app.modules.auth.schemas import (
    LoginResponse,
    SelectTenantRequest,
    TokenResponse,
    RefreshRequest
)
from app.modules.tenants.models import Tenant
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])
auth_service = AuthService()

@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return auth_service.login(db, data.username, data.password)

@router.post("/select-tenant", response_model=TokenResponse)
def select_tenant(
        data: SelectTenantRequest,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)):
    return auth_service.select_tenant(db, current_user["user_id"], data.tenant_id)

@router.get("/me")
def get_me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_id = current_user.get("tenant_id")

    user_context = current_user.copy()
    user_context["active_tenant"] = None

    if tenant_id:
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

        if not tenant.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant inactive"
            )

        user_context["active_tenant"] = {
            "id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug,
            "role": current_user.get("role")
        }

    return user_context

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(data: RefreshRequest):
    return auth_service.refresh_access_token(data.refresh_token)