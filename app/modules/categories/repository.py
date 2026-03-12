from sqlalchemy.orm import Session
from app.core.repositories.tenant_repository import BaseTenantRepository
from app.modules.categories.models import Category

class CategoryRepository(BaseTenantRepository):
    def __init__(self):
        super().__init__(Category)

    def update(self, db: Session, category: Category, data: dict) -> Category:
        for field, value in data.items():
            setattr(category, field, value)
        db.flush()
        return category