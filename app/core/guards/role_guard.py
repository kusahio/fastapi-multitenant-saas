from fastapi import Depends, HTTPException, status
from app.domain.enums.users_role import UserRole
from app.core.dependencies import get_current_user

class RoleGuard:
    def __init__(self, *allowed_roles: UserRole):
        self.allowed_roles = [role.value for role in allowed_roles]

    def __call__(self, current_user=Depends(get_current_user)):
        user_role = current_user.get("role")

        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes"
            )

        return current_user