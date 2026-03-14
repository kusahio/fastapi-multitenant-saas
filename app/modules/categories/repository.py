from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.repositories.tenant_repository import BaseTenantRepository
from app.modules.categories.models import Category
from app.modules.products.models import Product

class CategoryRepository(BaseTenantRepository):
    def __init__(self):
        super().__init__(Category)

    def update(self, db: Session, category: Category, data: dict) -> Category:
        for field, value in data.items():
            setattr(category, field, value)
        db.flush()
        return category
    
    def get_paginated(self, db: Session, tenant_id: int, skip: int, limit: int):
        total = db.query(func.count(Category.id)).filter(Category.tenant_id == tenant_id).scalar() or 0
        
        items = db.query(Category).filter(
            Category.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()
        
        return total, items

    def get_summary(self, db: Session, tenant_id: int):
        return db.query(
            Category.id,
            Category.name,
            func.count(Product.id).label('total_products')
        ).outerjoin(
            Product, Category.id == Product.category_id
        ).filter(
            Category.tenant_id == tenant_id
        ).group_by(
            Category.id
        ).all()