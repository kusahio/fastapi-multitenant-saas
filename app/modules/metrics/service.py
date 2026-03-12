from sqlalchemy.orm import Session
from sqlalchemy import func
from app.modules.products.models import Product
from app.modules.categories.models import Category

class MetricsService:
    def get_summary(self, db: Session, tenant_id: int):
        total_products = db.query(func.count(Product.id)).filter(
            Product.tenant_id == tenant_id,
            Product.active == True
        ).scalar() or 0

        total_categories = db.query(func.count(Category.id)).filter(
            Category.tenant_id == tenant_id,
            Category.active == True
        ).scalar() or 0

        products_by_category_query = db.query(
            Category.name.label('category_name'),
            func.count(Product.id).label('total_products')
        ).outerjoin(
            Product,
            (Category.id == Product.category_id) & (Product.active == True)
        ).filter(
            Category.tenant_id == tenant_id,
            Category.active == True
        ).group_by(
            Category.id
        ).all()

        products_by_category = [
            {
                "category_name": row.category_name,
                "total_products": row.total_products
            }
            for row in products_by_category_query
        ]

        return {
            "total_products": total_products,
            "total_categories": total_categories,
            "products_by_category": products_by_category
        }
