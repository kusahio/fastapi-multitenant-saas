from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.domain.enums.users_role import UserRole
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    document_number: Optional[str] = Field(None, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: UserRole

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
    role: Optional[UserRole] = None

class UserTenantResponse(BaseModel):
    tenant_id: int
    tenant_name: str
    tenant_slug: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)