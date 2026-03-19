from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import ProductCreate, ProductUpdate
from app.modules.products.models import Product

class ProductService:
    def __init__(self):
        self.repository = ProductRepository()
    
    def _change_status(self, db: Session, product_id: int, tenant_id: int, new_status: bool):
        product = self.get_by_id(db, product_id, tenant_id)
        product.active = new_status
        db.commit()
        db.refresh(product)
        return product

    def create(self, db: Session, data: ProductCreate, tenant_id: int):
        if data.barcode:
            existing = db.query(Product).filter(
                Product.tenant_id == tenant_id,
                Product.barcode == data.barcode
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un producto con este código de barras en tu tienda."
                )

        product = Product(**data.model_dump(), tenant_id=tenant_id)
        self.repository.save(db, product)
        db.commit()
        db.refresh(product)
        return product

    def get_list(self, db: Session, tenant_id: int):
        return self.repository.get_all(db, tenant_id)

    def get_paginated_list(
        self, db: Session, tenant_id: int, skip: int, limit: int,
        search: str | None = None,
        category_id: int | None = None,
        is_active: bool | None = None
    ):
        total, items = self.repository.get_paginated(
            db, tenant_id, skip, limit, search, category_id, is_active
        )
        return {"total": total, "items": items}

    def get_by_id(self, db: Session, product_id: int, tenant_id: int):
        product = self.repository.get_by_id(db, tenant_id, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        return product

    def update(self, db: Session, product_id: int, data: ProductUpdate, tenant_id: int):
        product = self.get_by_id(db, product_id, tenant_id)
        update_data = data.model_dump(exclude_unset=True)

        if "barcode" in update_data and update_data["barcode"]:
            existing = db.query(Product).filter(
                Product.tenant_id == tenant_id,
                Product.barcode == update_data["barcode"],
                Product.id != product_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=400, detail="El código de barras ya está en uso.")

        for key, value in update_data.items():
            setattr(product, key, value)

        db.commit()
        db.refresh(product)
        return product

    def delete(self, db: Session, product_id: int, tenant_id: int):
        deleted_product = self.repository.soft_delete(db, tenant_id, product_id)
        if not deleted_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Producto no encontrado"
            )
        db.commit()
        return deleted_product
    
    def deactivate(self, db: Session, product_id: int, tenant_id: int):
        return self._change_status(db, product_id, tenant_id, False)

    def activate(self, db: Session, product_id: int, tenant_id: int):
        return self._change_status(db, product_id, tenant_id, True)

    def find_for_pos(self, db: Session, tenant_id: int, query: str):
        results = self.repository.search_by_term(db, tenant_id, query)

        for product in results:
            if product.barcode == query:
                return [product]

        return results