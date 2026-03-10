from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.modules.tenants.repository import TenantRepository
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserUpdate
from app.modules.users.models import User
from app.domain.enums.users_role import UserRole
from app.domain.errors.tenant import TenantInactiveError
from app.domain.errors.users import UserAlreadyExistError, UserNotFoundError
from app.core.security import hashed_password, verify_password

class UserService:
  def __init__(self, user_repository: UserRepository, tenant_repository: TenantRepository):
    self.user_repository = user_repository
    self.tenant_repository = tenant_repository

  def _validate_role_creation(self, current_user: User, new_role: UserRole):
    if current_user.role == UserRole.PLATFORM_ADMIN:
      return
    
    if current_user.role == UserRole.OWNER:
      if new_role in (UserRole.ADMIN, UserRole.STAFF):
        return
      raise PermissionError('Invalid role assigment')
    
    if current_user.role == UserRole.ADMIN:
      if new_role == UserRole.STAFF:
        return
      raise PermissionError('Invalid role assigment')
    
    raise PermissionError('Insufficient permisions')
  
  def _validate_user_management_permissions(self, current_user: User, target_user: User):
    if current_user.role == UserRole.PLATFORM_ADMIN:
      return
    
    if current_user.tenant_id != target_user.tenant_id:
      raise PermissionError('Access denied')
    
    if (current_user.role == UserRole.OWNER and
        target_user.role == UserRole.OWNER):
      raise PermissionError('Owner cannot deactivate itself')
    
    if current_user.role == UserRole.OWNER:
      if target_user.role in (UserRole.ADMIN, UserRole.STAFF):
        return
      raise PermissionError('Invalid operation')
    
    if current_user.role == UserRole.ADMIN:
      if target_user.role == UserRole.STAFF:
        return
      raise PermissionError('Invalid operation')
    
    raise PermissionError('Insufficient permissions')

  def create_user(self, db: Session, data: UserCreate, current_user: User) -> User:
    normalized_email = data.email.lower().strip()
    
    self._validate_role_creation(current_user, data.role)

    tenant_id = current_user.tenant_id

    user = User(
      name = data.name,
      email = normalized_email,
      hashed_password = hashed_password(data.password),
      role = data.role,
      tenant_id = tenant_id,
      active = True
    )

    try:
      self.user_repository.save(db, user)
      db.commit()
      db.refresh(user)

      return user
    except IntegrityError:
      raise UserAlreadyExistError()
  
  def list_users(self, db: Session, current_user: User):
    if current_user.role == UserRole.PLATFORM_ADMIN:
      return self.user_repository.get_users(db)
    
    return self.user_repository.list_by_tenant(db, current_user.tenant_id)
  
  def update_user(self, db: Session, user_id: int, data: UserUpdate, current_user: User) -> User:
    user = self.user_repository.get_by_id(user_id)

    if not user:
      raise UserNotFoundError()
      
    if (current_user.role != UserRole.PLATFORM_ADMIN and 
        user.tenant_id != current_user.tenant_id
    ):
      raise PermissionError('Access denied')
      
    update_data = data.model_dump(exclude_unset=True)

    if 'role' in update_data:
      self._validate_role_creation(current_user, update_data['role'])
      
    if 'password' in update_data:
      update_data['password'] = hashed_password(update_data.pop('password'))

    try:
      self.user_repository.update(db, user, update_data)
      db.commit()
      db.refresh(user)

      return user
    
    except IntegrityError:
      db.rollback()
      raise ValueError('Update failed')
  
  def deactivate_user(self, db: Session, user_id: int, current_user: User) -> User:
    user = self.user_repository.get_by_id(db, user_id)

    if not user:
      raise UserNotFoundError()
    
    self._validate_user_management_permissions(current_user, user)

    try:
      user.active = False

      db.flush()

      if user.role == UserRole.OWNER:
        tenant = self.tenant_repository.get_by_id(db, user.tenant_id)

        if tenant:
          tenant.active = False
          db.flush()
      
      db.commit()
      return user
    
    except:
      db.rollback()
      raise
    
  def activate_user(self, db: Session, user_id: int, current_user: User) -> User:
    user = self.user_repository.get_by_id(db, user_id)

    if not user:
      raise UserNotFoundError()
    
    self._validate_user_management_permissions(current_user, user)

    try:
      user.active = True

      db.flush()

      if user.role == UserRole.OWNER:
        tenant = self.tenant_repository.get_by_id(db, user.tenant_id)

        if tenant:
          tenant.active = True
          db.flush()
      
      db.commit()
      return user
    
    except:
      db.rollback()
      raise