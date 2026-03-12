from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.guards.role_guard import RoleGuard
from app.domain.enums.users_role import UserRole
from app.modules.products.schemas import ProductCreate, ProductRead, ProductUpdate
from app.modules.products.service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])
product_service = ProductService()


@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN))]
)
def create_product(data: ProductCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return product_service.create(db, data, current_user["tenant_id"])


@router.get(
    "/",
    response_model=list[ProductRead],
    dependencies=[
        Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))]
)
def list_products(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return product_service.get_list(db, current_user["tenant_id"])


@router.patch(
    "/{product_id}",
    response_model=ProductRead,
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN))]
)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return product_service.update(db, product_id, data, current_user["tenant_id"])


@router.delete(
    "/{product_id}",
    response_model=ProductRead,
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN))]
)
def delete_product(product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return product_service.delete(db, product_id, current_user["tenant_id"])


@router.get("/search", response_model=list[ProductRead])
def search_products(
    q: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return product_service.find_for_pos(db, current_user.get("tenant_id"), q)
