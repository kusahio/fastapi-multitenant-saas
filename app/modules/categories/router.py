from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.guards.role_guard import RoleGuard
from app.domain.enums.users_role import UserRole
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
    status_code=status.HTTP_201_CREATED, dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN))]
)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return category_service.create(db, data, current_user["tenant_id"])

@router.get(
    "/", 
    response_model=list[CategoryRead], 
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))]
)
def list_categories(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return category_service.get_list(db, current_user["tenant_id"])

@router.get(
    "/", 
    response_model=PaginatedCategoriesResponse, 
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))]
)
def list_categories(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    return category_service.get_paginated_list(db, current_user.get("tenant_id"), skip, limit)

@router.get(
    "/summary", 
    response_model=list[CategorySummaryItem], 
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN, UserRole.STAFF))]
)
def get_categories_summary(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return category_service.get_summary(db, current_user.get("tenant_id"))

@router.patch(
    "/{category_id}", 
    response_model=CategoryRead, 
    dependencies=[Depends(RoleGuard(UserRole.OWNER, UserRole.ADMIN))]
)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return category_service.update(db, category_id, data, current_user["tenant_id"])

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
    return category_service.delete(db, category_id, current_user["tenant_id"])