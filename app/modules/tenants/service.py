from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.modules.tenants.repository import TenantRepository
from app.modules.tenants.schemas import TenantCreate, TenantUpdate
from app.modules.tenants.models import Tenant
from app.modules.users.models import User
from app.modules.user_tenants.models import UserTenant
from app.domain.enums.users_role import UserRole
from app.domain.errors.tenant import TenantAlreadyExistsError, TenantNotFoundError
from app.core.security import hashed_password

class TenantService:
    def __init__(self, tenant_repository: TenantRepository):
        self.tenant_repository = tenant_repository
    
    def create(self, db: Session, data: TenantCreate):

      tenant_data = data.model_dump(
          exclude={"owner_email", "owner_password"}
      )

      tenant_data["active"] = True

      tenant = Tenant(**tenant_data)

      try:
          self.tenant_repository.save(db, tenant)

          owner = User(
              email=data.owner_email.lower().strip(),
              hashed_password=hashed_password(data.owner_password),
              active=True
          )

          self.user_repository.save(db, owner)

          user_tenant = UserTenant(
              user_id=owner.id,
              tenant_id=tenant.id,
              role=UserRole.OWNER
          )

          self.user_tenant_repository.save(db, user_tenant)

          db.commit()

          return tenant

      except IntegrityError:
          db.rollback()
          raise TenantAlreadyExistsError()
    
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