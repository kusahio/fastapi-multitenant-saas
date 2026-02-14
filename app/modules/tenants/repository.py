from sqlalchemy.orm import Session
from app.modules.tenants.models import Tenant
from app.modules.tenants.schemas import TenantCreate

class TenantRepository:
  def create(self, db: Session, data: TenantCreate) -> Tenant:
    tenant = Tenant(
      name=data.name,
      slug=data.slug,
      bussiness_type=data.business_type,
    )

    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    return tenant