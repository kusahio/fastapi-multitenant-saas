from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.service import AuthService
from app.modules.auth.schemas import (
    LoginRequest,
    LoginResponse,
    SelectTenantRequest,
    TokenResponse
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])
auth_service = AuthService()

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, data.email, data.password)

@router.post("/select-tenant", response_model=TokenResponse)
def select_tenant(
        data: SelectTenantRequest,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)):
    return auth_service.select_tenant(db, current_user["user_id"], data.tenant_id)

@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return current_user