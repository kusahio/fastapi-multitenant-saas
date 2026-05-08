from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TenantOption(BaseModel):
    tenant_id: int
    name: str
    slug: str
    role: str

class LoginResponse(BaseModel):
    user_id: int
    name: str
    tenants: list[TenantOption]
    access_token: str
    refresh_token: str 

class SelectTenantRequest(BaseModel):
    tenant_id: int

class RefreshRequest(BaseModel):
    refresh_token: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str