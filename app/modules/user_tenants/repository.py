from sqlalchemy.orm import Session, joinedload
from app.modules.user_tenants.models import UserTenant

class UserTenantRepository:
    def save(self, db: Session, user_tenant: UserTenant) -> UserTenant:
        db.add(user_tenant)
        db.flush()
        return user_tenant

    def get_by_user_id(self, db: Session, user_id: int):
        return (
            db.query(UserTenant)
            .options(joinedload(UserTenant.tenant))
            .filter(UserTenant.user_id == user_id)
            .all()
        )

    def get_by_tenant_id(self, db: Session, tenant_id: int):
        return (
            db.query(UserTenant)
            .options(joinedload(UserTenant.user))
            .filter(UserTenant.tenant_id == tenant_id)
            .all()
        )

    def get_user_tenant(self, db: Session, user_id: int, tenant_id: int):
        return (
            db.query(UserTenant)
            .filter(
                UserTenant.user_id == user_id,
                UserTenant.tenant_id == tenant_id
            )
            .first()
        )