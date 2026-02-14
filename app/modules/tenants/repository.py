from sqlalchemy.orm import Session
from app.modules.tenants.models import Tenant
from app.modules.tenants.schemas import TenantCreate, TenantUpdate

class TenantRepository:
  def create(self, db: Session, data: TenantCreate) -> Tenant:
    tenant = Tenant(
      name=data.name,
      slug=data.slug,
      business_type=data.business_type,
    )

    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    return tenant
  
  def get_by_id(self, db: Session, tenant_id: int) -> Tenant | None:
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()

  def get_by_slug(self, db: Session, slug: str) -> Tenant | None:
      return db.query(Tenant).filter(Tenant.slug == slug).first()

  def list(self, db: Session) -> list[Tenant]:
      return db.query(Tenant).all()
  
  def update(self, db: Session, tenant: Tenant, data: TenantUpdate) -> Tenant:
    if data.name is not None:
        tenant.name = data.name
    if data.business_type is not None:
        tenant.business_type = data.business_type
    if data.active is not None:
        tenant.active = data.active
    
    db.commit()
    db.refresh(tenant)

    return tenant