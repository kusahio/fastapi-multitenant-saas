from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException, status, Response
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

AUTH_PATH = "/auth"

router = APIRouter(prefix=AUTH_PATH, tags=["Auth"])
auth_service = AuthService()

REFRESH_COOKIE_NAME = "refresh_token"
COOKIE_MAX_AGE = 7 * 24 * 60 * 60

def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
        path=AUTH_PATH,
    )

def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path=AUTH_PATH, samesite="lax")

@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    response: Response,
    data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    web: bool = False
):
    result = auth_service.login(db, data.username, data.password)
    refresh_token = getattr(result, "refresh_token", None) or result.get("refresh_token")

    if web:
        _set_refresh_cookie(response, refresh_token)
        
        if hasattr(result, "refresh_token"):
            result.refresh_token = ""
        else:
            result["refresh_token"] = ""
    
    return result

@router.post("/select-tenant", response_model=TokenResponse)
def select_tenant(
        request: Request,
        response: Response,
        data: SelectTenantRequest,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db),
        web: bool = False):
    
    result = auth_service.select_tenant(db, current_user.get("user_id"), data.tenant_id)
    refresh_token = getattr(result, "refresh_token", None) or result.get("refresh_token")

    if web:
        _set_refresh_cookie(response, refresh_token)

        if hasattr(result, "refresh_token"):
            result.refresh_token = ""
        else:
            result["refresh_token"] = ""

    return result

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
                detail="Tenant no encontrado"
            )

        if not tenant.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant inactivo"
            )

        user_context["active_tenant"] = {
            "id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug,
            "role": current_user.get("role")
        }

    return user_context

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    request: Request,
    response: Response,
    data: Optional[RefreshRequest] = None,
    web: bool = False
    ):

    token_from_cookie = request.cookies.get(REFRESH_COOKIE_NAME)
    token_from_body = data.refresh_token if data else None

    refresh_token_value = token_from_cookie or token_from_body

    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada, por favor inicia sesión nuevamente"
        )
    
    result = auth_service.refresh_access_token(refresh_token_value)
    new_refresh_token = getattr(result, "refresh_token", None) or result.get("refresh_token")

    if web or token_from_cookie:
        _set_refresh_cookie(response, new_refresh_token)
        if hasattr(result, "refresh_token"):
            result.refresh_token = ""
        else:
            result["refresh_token"] = ""
    return result

@router.post("/logout")
def logout(response: Response)-> dict:
    _clear_refresh_cookie(response)
    return {"detail": "Sesión cerrada exitosamente"}