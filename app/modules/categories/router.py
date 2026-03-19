from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.guards.role_guard import RoleGuard
from app.domain.enums.users_role import UserRole
from app.domain.errors.categories import CategoryNotFoundError, CategoryHasProductsError
from app.modules.categories.schemas import (
    CategoryCreate, CategoryRead, CategoryUpdate,
    PaginatedCategoriesResponse, CategorySummaryItem
)
from app.modules.categories.service import CategoryService


router = APIRouter(prefix="/categories", tags=["Categories"])
category_service = CategoryService()

@router.post(
    "/",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED, dependencies=[
        Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN))]
)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return category_service.create(db, data, current_user["tenant_id"])

@router.get(
    "/",
    response_model=PaginatedCategoriesResponse,
    dependencies=[
        Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))]
)
def list_categories(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return category_service.get_paginated_list(
        db, current_user.get("tenant_id"), skip, limit, search, is_active
    )

@router.get(
    "/summary",
    response_model=list[CategorySummaryItem],
    dependencies=[
        Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))]
)
def get_categories_summary(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return category_service.get_summary(db, current_user.get("tenant_id"))

@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN))]
)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return category_service.update(db, category_id, data, current_user["tenant_id"])
    except CategoryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se encontró la categoría"
        )

@router.delete(
    "/{category_id}",
    response_model=CategoryRead,
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN))]
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return category_service.delete(db, category_id, current_user.get("tenant_id"))
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró la categoría")
    except CategoryHasProductsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No se puede eliminar la categoría porque tiene productos asociados"
        )

@router.patch(
    "/{category_id}/deactivate",
    response_model=CategoryRead,
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN))]
)
def deactivate_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return category_service.deactivate(db, category_id, current_user["tenant_id"])
    except CategoryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se encontró la categoría"
        )

@router.patch(
    "/{category_id}/activate",
    response_model=CategoryRead,
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN))]
)
def activate_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return category_service.activate(db, category_id, current_user["tenant_id"])
    except CategoryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se encontró la categoría"
        )
