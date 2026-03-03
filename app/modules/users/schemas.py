from pydantic import BaseModel, EmailStr, Field
from app.domain.enums.users_role import UserRole
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
  name: str = Field(..., min_length=3, max_length=50)
  email: EmailStr
  role: UserRole

class UserCreate(UserBase):
  password: str = Field(..., min_length=6)

class UserRead(UserBase):
  id: int
  active: bool
  created_at: datetime

  class Config:
    from_attributes = True

class UserUpdate(BaseModel):
  name: Optional[str] = Field(None, min_length=3, max_length=50)
  email: Optional[EmailStr] = None
  password: Optional[str] = Field(None, min_length=6)
  role: Optional[UserRole] = None
  active: Optional[bool] = None