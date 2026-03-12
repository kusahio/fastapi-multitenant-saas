from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.guards.role_guard import RoleGuard
from app.domain.enums.users_role import UserRole
from app.modules.orders.schemas import OrderCreate, OrderRead
from app.modules.orders.service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])
order_service = OrderService()


@router.post(
    "/", response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))
    ]
)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return order_service.create_order(db, current_user.get("tenant_id"), current_user.get("user_id"), data)


@router.get(
    "/",
    response_model=list[OrderRead],
    dependencies=[
        Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))
    ]
)
def list_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return order_service.get_list(db, current_user.get("tenant_id"))


@router.get(
    "/{order_id}",
    response_model=OrderRead,
    dependencies=[
        Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))
    ]
)
def get_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return order_service.get_by_id(db, current_user.get("tenant_id"), order_id)
