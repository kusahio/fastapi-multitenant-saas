from pydantic import BaseModel
from app.domain.enums.business_type import BusinessType
from datetime import datetime
from typing import Optional

class TenantBase(BaseModel):
  name: str
  slug: str
  business_type: BusinessType

class TenantCreate(TenantBase):
  pass

class TenantRead(TenantBase):
  id: int
  active: bool
  created_at: datetime

  class Config:
    from_attributes = True

class TenantUpdate(BaseModel):
  name: Optional[str] = None
  business_type: Optional[BusinessType] = None
  active: Optional[bool] = None