from sqlalchemy.orm import Session
from app.modules.users.repository import UserRepository
from app.modules.user_tenants.repository import UserTenantRepository
from app.core.security import verify_password
from app.domain.errors.users import InvalidCredentialsError
from app.modules.auth.utils import create_access_token, create_refresh_token, decode_token
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
            access = create_access_token({
                "sub": str(user.id), 
                "role": UserRole.PLATFORM_ADMIN.value
            })
            refresh = create_refresh_token({
                "sub": str(user.id), 
                "role": UserRole.PLATFORM_ADMIN.value
            })
            return {
                "user_id": user.id, 
                "name": user.name, 
                "tenants": [],
                "access_token": access, 
                "refresh_token": refresh
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

        access = create_access_token({"sub": str(user.id)})
        refresh = create_refresh_token({"sub": str(user.id)})
        return {
            "user_id": user.id, 
            "name": user.name, 
            "tenants": tenants,
            "access_token": access, 
            "refresh_token": refresh
        }

    def select_tenant(self, db: Session, user_id: int, tenant_id: int):
        user_tenant = self.user_tenant_repository.get_user_tenant(db, user_id, tenant_id)
        
        if not user_tenant:
            raise InvalidCredentialsError()

        payload = {
            "sub": str(user_id), 
            "tenant_id": tenant_id, 
            "role": user_tenant.role.value
        }

        return {
            "access_token": create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
        }
    
    def refresh_access_token(self, db, refresh_token: str):
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise InvalidCredentialsError()
        
        new_payload = { k: v for k, v in payload.items() if k not in ("exp", "type")}

        return {
            "access_token": create_access_token(new_payload),
            "refresh_token": create_refresh_token(new_payload),
        }