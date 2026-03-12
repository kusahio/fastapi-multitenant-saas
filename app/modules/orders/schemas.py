from pydantic import BaseModel, Field, ConfigDict
from typing import List
from decimal import Decimal
from datetime import datetime

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: Decimal = Field(..., gt=0)

class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(..., min_length=1)

class OrderItemRead(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    discount: Decimal
    total_price: Decimal

    model_config = ConfigDict(from_attributes=True)

class OrderRead(BaseModel):
    id: int
    tenant_id: int
    user_id: int
    total: Decimal
    created_at: datetime
    items: List[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)