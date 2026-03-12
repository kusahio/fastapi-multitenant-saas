from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import ProductCreate, ProductUpdate
from app.modules.products.models import Product
from app.modules.categories.service import CategoryService

class ProductService:
    def __init__(self):
        self.repository = ProductRepository()
        self.category_service = CategoryService()

    def create(self, db: Session, data: ProductCreate, tenant_id: int):
        self.category_service.get_by_id(db, data.category_id, tenant_id)

        product_data = data.model_dump()
        product_data["tenant_id"] = tenant_id
        
        product = Product(**product_data)
        
        self.repository.save(db, product)
        db.commit()
        db.refresh(product)
        return product

    def get_list(self, db: Session, tenant_id: int):
        return self.repository.get_all(db, tenant_id)

    def get_by_id(self, db: Session, product_id: int, tenant_id: int):
        product = self.repository.get_by_id(db, tenant_id, product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    def update(self, db: Session, product_id: int, data: ProductUpdate, tenant_id: int):
        product = self.get_by_id(db, product_id, tenant_id)
        
        if data.category_id is not None:
            self.category_service.get_by_id(db, data.category_id, tenant_id)

        update_data = data.model_dump(exclude_unset=True)
        self.repository.update(db, product, update_data)
        db.commit()
        db.refresh(product)
        return product
        
    def delete(self, db: Session, product_id: int, tenant_id: int):
        deleted_product = self.repository.delete(db, tenant_id, product_id)
        if not deleted_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        db.commit()
        return deleted_product
    
    def find_for_pos(self, db: Session, tenant_id: int, query: str):
        results = self.repository.search_by_term(db, tenant_id, query)

        for product in results:
            if product.barcode == query:
                return [product]
                
        return results