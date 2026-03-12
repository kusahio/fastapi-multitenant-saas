from sqlalchemy.orm import Session
from app.core.repositories.tenant_repository import BaseTenantRepository
from app.modules.products.models import Product

class ProductRepository(BaseTenantRepository):
    def __init__(self):
        super().__init__(Product)

    def update(self, db: Session, product: Product, data: dict) -> Product:
        for field, value in data.items():
            setattr(product, field, value)
        db.flush()
        return product