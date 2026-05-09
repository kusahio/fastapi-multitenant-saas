from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.modules.categories.repository import CategoryRepository
from app.modules.categories.schemas import CategoryCreate, CategoryUpdate
from app.modules.categories.models import Category
from app.domain.errors.categories import CategoryNotFoundError, CategoryHasProductsError


class CategoryService:
    def __init__(self):
        self.repository = CategoryRepository()

    def _change_status(self, db: Session, category_id: int, tenant_id: int, new_status: bool):
        category = self.get_by_id(db, category_id, tenant_id)
        category.active = new_status
        db.commit()
        db.refresh(category)
        return category

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
        if not category or category.deleted_at is not None:
            raise CategoryNotFoundError()
        return category

    def update(self, db: Session, category_id: int, data: CategoryUpdate, tenant_id: int):
        category = self.get_by_id(db, category_id, tenant_id)
        update_data = data.model_dump(exclude_unset=True)

        self.repository.update(db, category, update_data)
        db.commit()
        db.refresh(category)
        return category

    def delete(self, db: Session, category_id: int, tenant_id: int):
        category = self.get_by_id(db, category_id, tenant_id)

        active_products = [
            product for product in category.products if product.deleted_at is None and product.active
        ]
        if active_products:
            raise CategoryHasProductsError()

        try:
            deleted_category = self.repository.soft_delete(
                db, tenant_id, category_id
            )

            if not deleted_category:
                raise CategoryNotFoundError()

            db.commit()
            return deleted_category

        except IntegrityError:
            db.rollback()
            raise CategoryHasProductsError()

    def deactivate(self, db: Session, category_id: int, tenant_id: int):
        return self._change_status(db, category_id, tenant_id, False)

    def activate(self, db: Session, category_id: int, tenant_id: int):
        return self._change_status(db, category_id, tenant_id, True)

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
