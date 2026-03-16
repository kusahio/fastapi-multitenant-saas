from sqlalchemy.orm import Session
from app.core.repositories.tenant_repository import BaseTenantRepository
from app.modules.orders.models import Order


class OrderRepository(BaseTenantRepository):
    def __init__(self):
        super().__init__(Order)

    def get_all(self, db: Session, tenant_id: int):
        return (
            db.query(self.model)
            .filter(self.model.tenant_id == tenant_id)
            .order_by(self.model.created_at.desc())
            .all()
        )