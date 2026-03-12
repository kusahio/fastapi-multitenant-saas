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

    def search_by_term(self, db: Session, tenant_id: int, term: str):
        return (
            db.query(self.model)
            .filter(
                self.model.tenant_id == tenant_id,
                self.model.active == True,
                (
                    (self.model.barcode == term) | 
                    (self.model.name.ilike(f"%{term}%"))
                )
            )
            .limit(10)
            .all()
        )
