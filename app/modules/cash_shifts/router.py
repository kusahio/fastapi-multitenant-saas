from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.guards.role_guard import RoleGuard
from app.domain.enums.users_role import UserRole
from app.modules.cash_shifts.schemas import CashShiftOpen, CashShiftClose, CashShiftRead
from app.modules.cash_shifts.service import CashShiftService

router = APIRouter(prefix="/cash-shifts", tags=["Cash Shifts"])
service = CashShiftService()

@router.post(
    "/open",
    response_model=CashShiftRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))
    ]
)
def open_shift(
    data: CashShiftOpen,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return service.open_shift(db, current_user.get("tenant_id"), current_user.get("user_id"), data)

@router.post(
    "/close",
    response_model=CashShiftRead,
    dependencies=[
        Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))
    ]
)
def close_shift(
    data: CashShiftClose,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return service.close_shift(db, current_user.get("tenant_id"), current_user.get("user_id"), data)

@router.get(
    "/active",
    response_model=CashShiftRead,
    dependencies=[
        Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))
    ]
)
def get_active_shift(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return service.get_active_shift_or_404(
        db,
        current_user.get("tenant_id"),
        current_user.get("user_id")
    )