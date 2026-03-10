from sqlalchemy.orm import Session
from app.modules.users.repository import UserRepository
from app.modules.tenants.repository import TenantRepository
from app.core.security import verify_password
from app.modules.auth.utils import create_access_token
from app.domain.errors.auth import InvalidCredentials

def AuthService():
  def __init__(self, db: Session):
    self.user_repository = UserRepository(db)
    self.tenant_repository = TenantRepository(db)
  
  def login(self, email: str, password: str):
    user = self.