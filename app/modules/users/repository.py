from sqlalchemy.orm import Session
from app.modules.users.models import User

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
  
  def get_by_email_tenant(self, db: Session, user_email: str, tenant_id: int) -> User | None:
    return db.query(User).filter(User.email == user_email, User.tenant_id == tenant_id).first()
  
  def get_users(self, db: Session) -> list[User]:
    return db.query(User).all()

  def list_by_tenant(self, db: Session, tenant_id: int):
    return db.query(User).filter(User.tenant_id == tenant_id).all()
  
  def update(self, db: Session, user: User, data: dict) -> User:
    for key, value in data.items():
      setattr(user, key, value)
    
    db.flush()

    return user