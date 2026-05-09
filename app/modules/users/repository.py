from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.modules.users.models import User
from app.modules.user_tenants.models import UserTenant

class UserRepository:
    def save(self, db: Session, user: User) -> User:
        db.add(user)
        db.flush()

        return user

    def get_by_id(self, db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str):
        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

    def get_users(self, db: Session) -> list[User]:
        return db.query(User).all()

    def update(self, db: Session, user: User, data: dict) -> User:
        for key, value in data.items():
            setattr(user, key, value)

        db.flush()

        return user

    def get_users_by_tenant_paginated(
        self, db: Session, tenant_id: int, skip: int = 0, limit: int = 100
    ):
        results = (
            db.query(User, UserTenant.role)
            .join(UserTenant, User.id == UserTenant.user_id)
            .filter(
                UserTenant.tenant_id == tenant_id,
                User.deleted_at == None
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

        users_with_roles = []
        for user, role in results:
            user_data = {column.name: getattr(
                user, column.name) for column in user.__table__.columns}
            user_data["role"] = role
            users_with_roles.append(user_data)

        return users_with_roles
    
    def soft_delete(self, db: Session, user_id: int) -> User | None:
        user = self.get_by_id(db, user_id)
        if user:
            user.deleted_at = datetime.now(timezone.utc)
            user.active = False
            db.flush()
        return user