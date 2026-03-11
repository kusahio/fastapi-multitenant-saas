from sqlalchemy.orm import Session


class BaseTenantRepository:

    def __init__(self, model):
        self.model = model

    def get_all(self, db: Session, tenant_id: int):
        return (
            db.query(self.model)
            .filter(self.model.tenant_id == tenant_id)
            .all()
        )

    def get_by_id(self, db: Session, tenant_id: int, entity_id: int):
        return (
            db.query(self.model)
            .filter(
                self.model.id == entity_id,
                self.model.tenant_id == tenant_id
            )
            .first()
        )

    def save(self, db: Session, entity):
        db.add(entity)
        db.flush()
        return entity

    def delete(self, db: Session, tenant_id: int, entity_id: int):
        entity = (
            db.query(self.model)
            .filter(
                self.model.id == entity_id,
                self.model.tenant_id == tenant_id
            )
            .first()
        )

        if entity:
            db.delete(entity)

        return entity