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
            **data.model_dump(),
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
                status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró la categoría")
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
                    detail="No se encontró la categoría"
                )

            db.commit()
            return deleted_category

        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar la categoría porque tiene productos agotados"
            )
    
    def get_paginated_list(
        self, db: Session, tenant_id: int, skip: int, limit: int, 
        search: str | None = None, is_active: bool | None = None
    ):
        total, items = self.repository.get_paginated(
            db, tenant_id, skip, limit, search, is_active
        )
        
        return {
            "total": total,
            "items": items
        }

    def get_summary(self, db: Session, tenant_id: int):
        summary_query = self.repository.get_summary(db, tenant_id)
        
        return [
            {
                "id": row.id,
                "name": row.name,
                "total_products": row.total_products
            }
            for row in summary_query
        ]