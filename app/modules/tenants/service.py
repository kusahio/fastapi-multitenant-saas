from sqlalchemy.orm import Session
from app.modules.tenants.repository import TenantRepository
from app.modules.tenants.schemas import TenantCreate, TenantUpdate
from app.modules.tenants.models import Tenant
from app.domain.errors.tenant import TenantAlreadyExistsError, TenantNotFoundError

class TenantService:
    def __init__(self, tenant_repository: TenantRepository):
        self.tenant_repository = tenant_repository
    
    def create(self, db: Session, data: TenantCreate) -> Tenant:
      existing = self.tenant_repository.get_by_slug(db, data.slug)

      if existing:
        raise TenantAlreadyExistsError()
      
      tenant = Tenant(**data.model_dump(), active=True)

      return self.tenant_repository.save(db, tenant)
    
    def get_by_id(self, db: Session, tenant_id: int) -> Tenant:
      tenant = self.tenant_repository.get_by_id(db, tenant_id)

      if not tenant:
        raise TenantNotFoundError()
      
      return tenant

    def update(self, db: Session, tenant_id: int, data: TenantUpdate) -> Tenant:
      tenant = self.get_by_id(db, tenant_id)
      updated_data = data.model_dump(exclude_unset=True)

      return self.tenant_repository.update(db, tenant, updated_data)
    
    def get_by_slug(self, db: Session, tenant_slug: str) -> Tenant:
      tenant = self.tenant_repository.get_by_slug(db, tenant_slug)

      if not tenant:
        raise TenantNotFoundError()
      
      return tenant
    
    def get_list(self, db: Session) -> list[Tenant]:
      tenants = self.tenant_repository.list(db)

      return tenants