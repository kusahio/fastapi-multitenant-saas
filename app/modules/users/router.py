from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.schemas import UserCreate, UserRead, UserUpdate
from app.modules.users.service import UserService
from app.modules.users.repository import UserRepository
from app.modules.user_tenants.repository import UserTenantRepository

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

user_service = UserService(
    UserRepository(),
    UserTenantRepository()
)

@router.post("/", response_model=UserRead)
def create_user(
    data: UserCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return user_service.create_user(db, data, current_user)

@router.get("/", response_model=list[UserRead])
def list_users(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return user_service.list_users(db, current_user)

@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    data: UserUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return user_service.update_user(
        db,
        user_id,
        data,
        current_user
    )

@router.delete("/{user_id}")
def deactivate_user(
    user_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return user_service.deactivate_user(
        db,
        user_id,
        current_user
    )