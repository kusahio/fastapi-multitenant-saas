from sqlalchemy.orm import Session
from app.modules.users.repository import UserRepository
from app.modules.user_tenants.repository import UserTenantRepository
from app.core.security import verify_password
from app.domain.errors.users import InvalidCredentialsError
from app.modules.auth.utils import create_access_token
from app.domain.enums.users_role import UserRole

class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.user_tenant_repository = UserTenantRepository()

    def login(self, db: Session, email: str, password: str):
        user = self.user_repository.get_by_email(db, email)

        if not user:
            raise InvalidCredentialsError()

        if not user.active:
            raise InvalidCredentialsError()

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        if user.is_platform_admin:
            token = create_access_token({
                "sub": str(user.id),
                "role": UserRole.PLATFORM_ADMIN.value,
            })
            return {
                "user_id": user.id,
                "name": user.name,
                "tenants": [],
                "access_token": token
            }

        user_tenants = self.user_tenant_repository.get_by_user_id(
            db,
            user.id
        )

        tenants = []

        for user_tenant in user_tenants:
            tenants.append({
                "tenant_id": user_tenant.tenant.id,
                "name": user_tenant.tenant.name,
                "slug": user_tenant.tenant.slug,
                "role": user_tenant.role.value
            })

        token = create_access_token({
            "sub": str(user.id)
        })

        return {
            "user_id": user.id,
            "name": user.name,
            "tenants": tenants,
            "access_token": token
        }

    def select_tenant(self, db: Session, user_id: int, tenant_id: int):
        user_tenant = self.user_tenant_repository.get_user_tenant(db, user_id, tenant_id)
        
        if not user_tenant:
            raise InvalidCredentialsError()

        token = create_access_token({
            "sub": str(user_id),
            "tenant_id": tenant_id,
            "role": user_tenant.role.value
        })

        return {
            "access_token": token
        }