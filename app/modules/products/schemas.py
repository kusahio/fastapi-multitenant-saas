from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal
from app.domain.enums.unit_type import UnitType

class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    discount: Optional[Decimal] = Field(None, ge=0)
    stock: Decimal = Field(default=0, ge=0)
    unit_type: UnitType = UnitType.UNIT
    category_id: int
    active: Optional[bool] = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    discount: Decimal = Field(default=0, ge=0)
    is_discount_active: Optional[bool] = None
    stock: Optional[Decimal] = Field(None, ge=0)
    unit_type: Optional[UnitType] = None
    category_id: Optional[int] = None
    active: Optional[bool] = None

class ProductRead(ProductBase):
    id: int
    tenant_id: int

    model_config = ConfigDict(from_attributes=True)