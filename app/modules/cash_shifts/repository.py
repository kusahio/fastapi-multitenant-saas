from sqlalchemy.orm import Session
from app.core.repositories.tenant_repository import BaseTenantRepository
from app.modules.cash_shifts.models import CashShift, CashShiftStatus

class CashShiftRepository(BaseTenantRepository):
    def __init__(self):
        super().__init__(CashShift)

    def get_active_shift(self, db: Session, tenant_id: int, user_id: int):
        return (
            db.query(self.model)
            .filter(
                self.model.tenant_id == tenant_id,
                self.model.user_id == user_id,
                self.model.status == CashShiftStatus.OPEN
            )
            .first()
        )