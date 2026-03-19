from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.guards.role_guard import RoleGuard
from app.domain.enums.users_role import UserRole
from app.domain.errors.products import ProductNotFoundError, ProductBarcodeAlreadyExistsError
from app.modules.products.schemas import ProductCreate, ProductRead, ProductUpdate, PaginatedProductsResponse
from app.modules.products.service import ProductService
from app.domain.enums.unit_type import UnitType

router = APIRouter(prefix="/products", tags=["Products"])
product_service = ProductService()

@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN))]
)
def create_product(data: ProductCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return product_service.create(db, data, current_user["tenant_id"])
    except ProductBarcodeAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Ya existe un producto con este código de barras en tu tienda."
        )

@router.get(
    "/",
    response_model=PaginatedProductsResponse,
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))]
)
def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return product_service.get_paginated_list(
        db, current_user.get("tenant_id"), skip, limit, search, category_id, is_active
    )

@router.get(
    "/search",
    response_model=list[ProductRead],
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))]
)
def search_products(q: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return product_service.find_for_pos(db, current_user.get("tenant_id"), q)

@router.get(
    "/unit-types",
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))]
)
def get_unit_types():
    return [unit.value for unit in UnitType]

@router.patch(
    "/{product_id}",
    response_model=ProductRead,
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN))]
)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return product_service.update(db, product_id, data, current_user["tenant_id"])
    except ProductNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Producto no encontrado"
        )
    except ProductBarcodeAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de barras ya está en uso."
        )

@router.delete(
    "/{product_id}",
    response_model=ProductRead,
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN))]
)
def delete_product(product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return product_service.delete(db, product_id, current_user["tenant_id"])
    except ProductNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Producto no encontrado"
        )

@router.patch(
    "/{product_id}/deactivate",
    response_model=ProductRead,
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN))]
)
def deactivate_product(product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return product_service.deactivate(db, product_id, current_user["tenant_id"])
    except ProductNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Producto no encontrado"
        )

@router.patch(
    "/{product_id}/activate",
    response_model=ProductRead,
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN))]
)
def activate_product(product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return product_service.activate(db, product_id, current_user["tenant_id"])
    except ProductNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Producto no encontrado"
        )