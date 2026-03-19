from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.domain.enums.tenant_role import TenantRole
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    document_number: Optional[str] = Field(None, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: TenantRole

class UserRead(UserBase):
    id: int
    active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    document_number: Optional[str] = Field(None, max_length=50)
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[TenantRole] = None

class UserTenantResponse(BaseModel):
    tenant_id: int
    tenant_name: str
    tenant_slug: str
    role: TenantRole

    model_config = ConfigDict(from_attributes=True)

class UserWithRoleRead(UserRead):
    role: TenantRole