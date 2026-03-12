from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional
from app.modules.cash_shifts.models import CashShiftStatus

class CashShiftOpen(BaseModel):
    opening_balance: Decimal = Field(..., ge=0)

class CashShiftClose(BaseModel):
    closing_balance: Decimal = Field(..., ge=0)
    observations: Optional[str] = None

class CashShiftRead(BaseModel):
    id: int
    user_id: int
    opening_balance: Decimal
    closing_balance: Optional[Decimal]
    expected_balance: Optional[Decimal]
    status: CashShiftStatus
    opened_at: datetime
    closed_at: Optional[datetime]
    observations: Optional[str]

    model_config = ConfigDict(from_attributes=True)