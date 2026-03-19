from enum import Enum

class TenantRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    STAFF = "staff"