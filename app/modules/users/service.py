from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.modules.users.repository import UserRepository
from app.modules.user_tenants.repository import UserTenantRepository
from app.modules.users.schemas import UserCreate, UserUpdate
from app.modules.users.models import User
from app.modules.user_tenants.models import UserTenant
from app.domain.enums.users_role import UserRole
from app.domain.errors.users import UserAlreadyExistError, UserNotFoundError, InsufficientPermissionsError
from app.core.security import hashed_password

class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        user_tenant_repository: UserTenantRepository
    ):
        self.user_repository = user_repository
        self.user_tenant_repository = user_tenant_repository

    def _validate_role_creation(self, current_user, new_role: UserRole):
        role = current_user["role"]

        if role == UserRole.PLATFORM_ADMIN:
            return

        if role == UserRole.OWNER:
            if new_role in (UserRole.ADMIN, UserRole.STAFF):
                return
            raise InsufficientPermissionsError()

        if role == UserRole.ADMIN:
            if new_role == UserRole.STAFF:
                return
            raise InsufficientPermissionsError()

        raise InsufficientPermissionsError()
    
    def _validate_user_management_permissions(self, current_user, target_role):
        role = current_user["role"]

        if role == UserRole.PLATFORM_ADMIN:
            return

        if role == UserRole.OWNER:
            if target_role in (UserRole.ADMIN, UserRole.STAFF):
                return
            raise InsufficientPermissionsError()

        if role == UserRole.ADMIN:
            if target_role == UserRole.STAFF:
                return
            raise InsufficientPermissionsError()

        raise InsufficientPermissionsError()

    def create_user(self, db: Session, data: UserCreate, current_user):
        tenant_id = current_user["tenant_id"]
        normalized_email = data.email.lower().strip()
        self._validate_role_creation(current_user, data.role)

        try:
            user = User(
                name=data.name,
                email=normalized_email,
                hashed_password=hashed_password(data.password),
                active=True
            )

            self.user_repository.save(db, user)

            db.flush()

            user_tenant = UserTenant(
                user_id=user.id,
                tenant_id=tenant_id,
                role=data.role
            )

            self.user_tenant_repository.save(db, user_tenant)

            db.commit()
            db.refresh(user)

            return user

        except IntegrityError:
            db.rollback()
            raise UserAlreadyExistError()

    def list_users(self, db: Session, current_user):
        tenant_id = current_user["tenant_id"]

        user_tenants = self.user_tenant_repository.get_by_tenant_id(
            db,
            tenant_id
        )

        return [user_tenant.user for user_tenant in user_tenants]

    def update_user(self, db: Session, user_id: int, data: UserUpdate, current_user):
        tenant_id = current_user["tenant_id"]

        user_tenant = self.user_tenant_repository.get_user_tenant(
            db,
            user_id,
            tenant_id
        )

        if not user_tenant:
            raise UserNotFoundError()

        user = user_tenant.user

        update_data = data.model_dump(exclude_unset=True)

        if "role" in update_data:
            self._validate_role_creation(current_user, update_data["role"])
            user_tenant.role = update_data.pop("role")

        if "password" in update_data:
            update_data["hashed_password"] = hashed_password(
                update_data.pop("password")
            )

        try:
            self.user_repository.update(
                db,
                user,
                update_data
            )

            db.commit()
            db.refresh(user)

            return user

        except IntegrityError:
            db.rollback()
            raise ValueError("Update failed")

    def deactivate_user(self, db: Session, user_id: int, current_user):
        tenant_id = current_user["tenant_id"]

        user_tenant = self.user_tenant_repository.get_user_tenant(
            db,
            user_id,
            tenant_id
        )

        if not user_tenant:
            raise UserNotFoundError()

        self._validate_user_management_permissions(
            current_user,
            user_tenant.role
        )

        try:
            user_tenant.user.active = False

            db.commit()

            return user_tenant.user

        except Exception:
            db.rollback()
            raise

    def activate_user(self, db: Session, user_id: int, current_user):
        tenant_id = current_user["tenant_id"]

        user_tenant = self.user_tenant_repository.get_user_tenant(
            db,
            user_id,
            tenant_id
        )

        if not user_tenant:
            raise UserNotFoundError()

        self._validate_user_management_permissions(
            current_user,
            user_tenant.role
        )

        try:
            user_tenant.user.active = True

            db.commit()

            return user_tenant.user

        except Exception:
            db.rollback()
            raise
    
    def get_user_tenants(self, db: Session, user_id: int):
        user_tenants = self.user_tenant_repository.get_by_user_id(db, user_id)

        return [
            {
                "tenant_id": user_tenant.tenant.id,
                "tenant_name": user_tenant.tenant.name,
                "tenant_slug": user_tenant.tenant.slug,
                "role": user_tenant.role
            }
            for user_tenant in user_tenants
        ]