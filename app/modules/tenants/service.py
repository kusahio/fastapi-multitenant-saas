from sqlalchemy.orm import Session
from app.modules.tenants.repository import TenantRepository
from app.modules.tenants.schemas import TenantCreate
from app.modules.tenants.models import Tenant
from app.domain.errors.tenant import TenantAlreadyExistsError

class TenantService:
    def __init__(self, tenant_repository: TenantRepository):
        self.tenant_repository = tenant_repository
    
    def create(self, db: Session, data: TenantCreate) -> Tenant:
      existing = self.tenant_repository.get_by_slug(db, data.slug)

      if existing:
        raise TenantAlreadyExistsError()
      
      tenant = Tenant(**data.model_dump(), active=True)

      return self.tenant_repository.save(db, tenant)