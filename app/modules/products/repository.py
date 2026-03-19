from datetime import datetime, timezone
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

    def get_paginated(
        self, db: Session, tenant_id: int, skip: int, limit: int,
        search: str | None = None,
        category_id: int | None = None,
        is_active: bool | None = None
    ):
        query = db.query(self.model).filter(
            self.model.tenant_id == tenant_id,
            self.model.deleted_at == None
        )

        if search:
            query = query.filter(self.model.name.ilike(f"%{search}%"))

        if category_id is not None:
            query = query.filter(self.model.category_id == category_id)

        if is_active is not None:
            query = query.filter(self.model.active == is_active)

        total = query.count()
        items = query.order_by(self.model.id.desc()).offset(skip).limit(limit).all()

        return total, items

    def search_by_term(self, db: Session, tenant_id: int, term: str):
        return (
            db.query(self.model)
            .filter(
                self.model.tenant_id == tenant_id,
                self.model.active == True,
                self.model.deleted_at == None,
                (
                    (self.model.barcode == term) | 
                    (self.model.name.ilike(f"%{term}%"))
                )
            )
            .limit(10)
            .all()
        )
    
    def get_by_id_for_update(self, db: Session, tenant_id: int, product_id: int):
        """
        Busca un producto y bloquea la fila en la base de datos 
        hasta que termine la transacción actual (commit o rollback).
        """
        return (
            db.query(self.model)
            .filter(
                self.model.tenant_id == tenant_id,
                self.model.id == product_id,
                self.model.deleted_at == None
            )
            .with_for_update()
            .first()
        )
    
    def soft_delete(self, db: Session, tenant_id: int, entity_id: int):
        entity = (
            db.query(self.model)
            .filter(
                self.model.id == entity_id,
                self.model.tenant_id == tenant_id,
                self.model.deleted_at == None
            )
            .first()
        )
        if entity:
            entity.deleted_at = datetime.now(timezone.utc)
            db.flush()
        return entity