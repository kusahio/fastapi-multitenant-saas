from enum import Enum

class UserRole(str, Enum):
  PLATFORM_ADMIN = 'platform_admin'
  OWNER = 'owner'
  ADMIN = 'admin'
  STAFF = 'staff'