from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.guards.role_guard import RoleGuard
from app.domain.enums.users_role import UserRole
from app.modules.users.schemas import UserCreate, UserRead, UserUpdate
from app.modules.users.service import UserService
from app.modules.users.repository import UserRepository
from app.modules.user_tenants.repository import UserTenantRepository
from app.modules.cash_shifts.repository import CashShiftRepository
from app.domain.errors.users import UserAlreadyExistError, UserNotFoundError, UserHasOpenShiftError
from app.modules.users.schemas import UserTenantResponse
from app.modules.users.schemas import UserWithRoleRead

router = APIRouter(prefix="/users", tags=["Users"])

user_service = UserService(
    UserRepository(),
    UserTenantRepository(),
    CashShiftRepository()
)

@router.post(
    "/", response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(RoleGuard(UserRole.PLATFORM_ADMIN,
                UserRole.OWNER, UserRole.ADMIN))
    ]
)
def create_user(
    data: UserCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return user_service.create_user(db, data, current_user)
    except UserAlreadyExistError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con este email"
        )

@router.get(
    "/",
    response_model=list[UserWithRoleRead],
    dependencies=[Depends(
        RoleGuard(UserRole.PLATFORM_ADMIN, UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))
    ]
)
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    tenant_id = current_user.get("tenant_id")
    return user_service.list_users(db, tenant_id, skip=skip, limit=limit)


@router.get("/me/tenants", response_model=list[UserTenantResponse])
def get_my_tenants(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return user_service.get_user_tenants(db, current_user["user_id"])


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[
        Depends(RoleGuard(UserRole.PLATFORM_ADMIN,
                UserRole.OWNER, UserRole.ADMIN))
    ]
)
def update_user(
    user_id: int,
    data: UserUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return user_service.update_user(db, user_id, data, current_user)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el usuario"
        )


@router.delete(
    "/{user_id}",
    dependencies=[
        Depends(RoleGuard(UserRole.PLATFORM_ADMIN,
                UserRole.OWNER, UserRole.ADMIN))
    ]
)
def deactivate_user(
    user_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return user_service.deactivate_user(db, user_id, current_user)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el usuario"
        )
    
    except UserHasOpenShiftError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El usuario tiene una caja abierta. Debe cerrarla antes de desactivar."
        )


@router.patch(
    "/{user_id}/activate",
    response_model=UserRead,
    dependencies=[
        Depends(RoleGuard(UserRole.PLATFORM_ADMIN,
                UserRole.OWNER, UserRole.ADMIN))
    ]
)
def activate_user(
    user_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return user_service.activate_user(db, user_id, current_user)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el usuario"
        )