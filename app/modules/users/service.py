from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.modules.users.repository import UserRepository
from app.modules.user_tenants.repository import UserTenantRepository
from app.modules.users.schemas import UserCreate, UserUpdate
from app.modules.users.models import User
from app.modules.user_tenants.models import UserTenant
from app.domain.enums.users_role import UserRole
from app.domain.enums.tenant_role import TenantRole
from app.domain.errors.users import (
    UserAlreadyExistError,
    UserNotFoundError,
    InsufficientPermissionsError,
    UserHasOpenShiftError
)
from app.core.security import hashed_password
from app.modules.cash_shifts.repository import CashShiftRepository

class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        user_tenant_repository: UserTenantRepository,
        cash_shift_repository: CashShiftRepository
    ):
        self.user_repository = user_repository
        self.user_tenant_repository = user_tenant_repository
        self.cash_shift_repository = cash_shift_repository

    def _validate_role_creation(self, current_user, new_role: TenantRole):
        role = current_user.get("role")

        if role == UserRole.PLATFORM_ADMIN:
            return

        if role == UserRole.OWNER:
            if new_role in (TenantRole.ADMIN, TenantRole.STAFF):
                return
            raise InsufficientPermissionsError()

        if role == UserRole.ADMIN:
            if new_role == TenantRole.STAFF:
                return
            raise InsufficientPermissionsError()

        raise InsufficientPermissionsError()
    
    def _validate_user_management_permissions(self, current_user, target_role):
        role = current_user.get("role")

        if role == UserRole.PLATFORM_ADMIN:
            return

        if role == UserRole.OWNER:
            if target_role in (TenantRole.ADMIN, TenantRole.STAFF):
                return
            raise InsufficientPermissionsError()

        if role == UserRole.ADMIN:
            if target_role == TenantRole.STAFF:
                return
            raise InsufficientPermissionsError()

        raise InsufficientPermissionsError()

    def _check_user_has_open_shift(self, db: Session, user_id: int, tenant_id: int):
        active_shift = self.cash_shift_repository.get_active_shift(db, tenant_id, user_id)
        if active_shift:
            raise UserHasOpenShiftError()
    
    def _change_user_status(self, db: Session, user_id: int, current_user, new_status: bool):
        if current_user.get("role") == UserRole.PLATFORM_ADMIN:
            user = self.user_repository.get_by_id(db, user_id)
            if not user:
                raise UserNotFoundError()
            
            if not new_status and user.deleted_at is None:
                user_tenants = self.user_tenant_repository.get_by_user_id(db, user_id)
                for ut in user_tenants:
                    self._check_user_has_open_shift(db, user_id, ut.tenant_id)
            
            user.active = new_status
            db.commit()
            return user

        tenant_id = current_user.get("tenant_id")
        user_tenant = self.user_tenant_repository.get_user_tenant(
            db, user_id, tenant_id
        )

        if not user_tenant:
            raise UserNotFoundError()
        
        if not new_status and user_tenant.user.deleted_at is None:
            self._check_user_has_open_shift(db, user_id, tenant_id)

        self._validate_user_management_permissions(
            current_user, user_tenant.role
        )

        try:
            user_tenant.user.active = new_status
            db.commit()
            return user_tenant.user
        except Exception:
            db.rollback()
            raise

    def create_user(self, db: Session, data: UserCreate, current_user):
        normalized_email = data.email.lower().strip()
        self._validate_role_creation(current_user, data.role)

        if current_user.get("role") == UserRole.PLATFORM_ADMIN and data.role == UserRole.PLATFORM_ADMIN:
            try:
                user = User(
                    name=data.name,
                    email=normalized_email,
                    document_number=data.document_number,
                    hashed_password=hashed_password(data.password),
                    is_platform_admin=True,
                    active=True
                )
                self.user_repository.save(db, user)
                db.commit()
                db.refresh(user)
                return user
            except IntegrityError:
                db.rollback()
                raise UserAlreadyExistError()

        tenant_id = current_user.get("tenant_id")
        
        try:
            user = User(
                name=data.name,
                email=normalized_email,
                document_number=data.document_number,
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

    def list_users(self, db: Session, tenant_id: int, skip: int = 0, limit: int = 100):
        return self.user_repository.get_users_by_tenant_paginated(db, tenant_id, skip, limit)

    def update_user(self, db: Session, user_id: int, data: UserUpdate, current_user):
        is_platform_admin = current_user.get("role") == UserRole.PLATFORM_ADMIN

        if is_platform_admin:
            user = self.user_repository.get_by_id(db, user_id)
            if not user:
                raise UserNotFoundError()
            user_tenant = None
        else:
            tenant_id = current_user.get("tenant_id")
            user_tenant = self.user_tenant_repository.get_user_tenant(
                db, user_id, tenant_id
            )
            if not user_tenant:
                raise UserNotFoundError()
            user = user_tenant.user

        update_data = data.model_dump(exclude_unset=True)

        if "role" in update_data:
            if is_platform_admin:
                update_data.pop("role")
            else:
                self._validate_role_creation(current_user, update_data["role"])
                user_tenant.role = update_data.pop("role")

        if "password" in update_data:
            update_data["hashed_password"] = hashed_password(
                update_data.pop("password")
            )

        try:
            self.user_repository.update(db, user, update_data)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise ValueError("Actualización fallida")

    def deactivate_user(self, db: Session, user_id: int, current_user):
        self._change_user_status(db, user_id, current_user, new_status=False)

        user = self.user_repository.soft_delete(db, user_id)
        if not user:
            raise UserNotFoundError()

        db.commit()
        return user

    def activate_user(self, db: Session, user_id: int, current_user):
        if current_user.get("role") == UserRole.PLATFORM_ADMIN:
            user = self.user_repository.get_by_id(db, user_id)
            if not user:
                raise UserNotFoundError()

            user.active = True
            user.deleted_at = None
            db.commit()
            return user

        tenant_id = current_user.get("tenant_id")
        user_tenant = self.user_tenant_repository.get_user_tenant(
            db, user_id, tenant_id
        )

        if not user_tenant:
            raise UserNotFoundError()

        self._validate_user_management_permissions(
            current_user, user_tenant.role
        )

        try:
            user_tenant.user.active = True
            user_tenant.user.deleted_at = None
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