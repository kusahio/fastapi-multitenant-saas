from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    active: Optional[bool] = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    active: Optional[bool] = None

class CategoryRead(CategoryBase):
    id: int
    tenant_id: int

    model_config = ConfigDict(from_attributes=True)