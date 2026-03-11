from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TenantOption(BaseModel):
    tenant_id: int
    slug: str
    role: str

class LoginResponse(BaseModel):
    user_id: int
    tenants: list[TenantOption]
    access_token: str

class SelectTenantRequest(BaseModel):
    tenant_id: int

class TokenResponse(BaseModel):
    access_token: str