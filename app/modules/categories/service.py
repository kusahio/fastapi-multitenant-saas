from sqlalchemy.orm import Session
from app.modules.categories.repository import CategoryRepository
from app.modules.categories.schemas import CategoryCreate, CategoryUpdate
from app.modules.categories.models import Category
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


class CategoryService:
    def __init__(self):
        self.repository = CategoryRepository()

    def create(self, db: Session, data: CategoryCreate, tenant_id: int):
        category = Category(
            name=data.name,
            active=data.active,
            tenant_id=tenant_id
        )
        self.repository.save(db, category)
        db.commit()
        db.refresh(category)
        return category

    def get_list(self, db: Session, tenant_id: int):
        return self.repository.get_all(db, tenant_id)

    def get_by_id(self, db: Session, category_id: int, tenant_id: int):
        category = self.repository.get_by_id(db, tenant_id, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return category

    def update(self, db: Session, category_id: int, data: CategoryUpdate, tenant_id: int):
        category = self.get_by_id(db, category_id, tenant_id)
        update_data = data.model_dump(exclude_unset=True)

        self.repository.update(db, category, update_data)
        db.commit()
        db.refresh(category)
        return category

    def delete(self, db: Session, category_id: int, tenant_id: int):
        try:
            deleted_category = self.repository.delete(
                db, tenant_id, category_id)

            if not deleted_category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )

            db.commit()
            return deleted_category

        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete this category because it has associated products."
            )
