from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    discount: Decimal = Field(default=0, ge=0)
    is_discount_cumulative: Optional[bool] = False
    is_discount_active: Optional[bool] = False
    active: Optional[bool] = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    discount: Optional[Decimal] = Field(None, ge=0)
    is_discount_cumulative: Optional[bool] = None
    is_discount_active: Optional[bool] = None
    active: Optional[bool] = None

class CategoryRead(CategoryBase):
    id: int
    tenant_id: int

    model_config = ConfigDict(from_attributes=True)

class CategorySummaryItem(BaseModel):
    id: int
    name: str
    total_products: int

class PaginatedCategoriesResponse(BaseModel):
    total: int
    items: list[CategoryRead]