from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from fastapi import HTTPException, status
from datetime import datetime, timezone
from app.modules.cash_shifts.repository import CashShiftRepository
from app.modules.orders.models import Order
from app.modules.cash_shifts.models import CashShift, CashShiftStatus
from app.modules.cash_shifts.schemas import CashShiftOpen, CashShiftClose

class CashShiftService:
    def __init__(self):
        self.repository = CashShiftRepository()

    def open_shift(self, db: Session, tenant_id: int, user_id: int, data: CashShiftOpen):
        if self.repository.get_active_shift(db, tenant_id, user_id):
            raise HTTPException(status_code=400, detail="Ya tienes una caja abierta.")
        
        shift = CashShift(
            tenant_id=tenant_id,
            user_id=user_id,
            opening_balance=data.opening_balance,
            status=CashShiftStatus.OPEN
        )
        self.repository.save(db, shift)
        db.commit()
        return shift

    def close_shift(self, db: Session, tenant_id: int, user_id: int, data: CashShiftClose):
        shift = self.repository.get_active_shift(db, tenant_id, user_id)
        if not shift:
            raise HTTPException(status_code=404, detail="No tienes ninguna caja abierta.")

        total_sales = db.query(func.sum(Order.total)).filter(
            Order.cash_shift_id == shift.id,
            Order.tenant_id == tenant_id
        ).scalar() or Decimal('0.00')

        shift.expected_balance = shift.opening_balance + total_sales
        shift.closing_balance = data.closing_balance
        shift.status = CashShiftStatus.CLOSED
        shift.closed_at = datetime.now(timezone.utc)
        shift.observations = data.observations

        db.commit()
        db.refresh(shift)
        return shift
    
    def get_active_shift_or_404(self, db: Session, tenant_id: int, user_id: int):
        shift = self.repository.get_active_shift(db, tenant_id, user_id)
        if not shift:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No tienes una caja abierta actualmente."
            )
        return shift