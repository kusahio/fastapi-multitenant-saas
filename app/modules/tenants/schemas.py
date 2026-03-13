from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from app.domain.enums.business_type import BusinessType
from datetime import datetime
from typing import Optional

class TenantBase(BaseModel):
    name: str
    slug: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r'^[a-z0-9]+(-[a-z0-9]+)*$'
    )
    business_type: BusinessType

    @field_validator('slug')
    @classmethod
    def normalize_slug(cls, value: str) -> str:
        value = value.lower().strip()
        return value

class TenantCreate(TenantBase):
    owner_name: str
    owner_email: EmailStr
    owner_password: str
    owner_document_number: Optional[str] = Field(None, max_length=50)

class TenantRead(TenantBase):
    id: int
    active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    business_type: Optional[BusinessType] = None
    active: Optional[bool] = None