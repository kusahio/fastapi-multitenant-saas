from sqlalchemy.orm import Session
from app.modules.tenants.models import Tenant

class TenantRepository:
  def save(self, db: Session, tenant: Tenant) -> Tenant:

    db.add(tenant)
    db.flush()

    return tenant
  
  def get_by_id(self, db: Session, tenant_id: int) -> Tenant | None:
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()

  def get_by_slug(self, db: Session, slug: str) -> Tenant | None:
      return db.query(Tenant).filter(Tenant.slug == slug).first()

  def list(self, db: Session) -> list[Tenant]:
      return db.query(Tenant).all()
  
  def update(self, db: Session, tenant: Tenant, data: dict) -> Tenant:
    for field, value in data.items():
      setattr(tenant, field, value)
    
    db.flush()

    return tenant