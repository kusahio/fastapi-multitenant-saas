from sqlalchemy import (
  Column, 
  String, 
  Boolean, 
  Integer, 
  DateTime, 
  ForeignKey, 
  UniqueConstraint, 
  func,  
  Enum as SQLEnum,
  Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.domain.enums.users_role import UserRole

class User(Base):
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True, index=True)
  email = Column(String, nullable=False)
  hashed_password = Column(String, nullable=False)
  role = Column(SQLEnum(UserRole), nullable=False)
  tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)
  tenant = relationship('Tenant', back_populates='users')
  active = Column(Boolean, default=True, nullable=False)
  created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

  __table_args__ = (
    UniqueConstraint('email', 'tenant_id', name='uq_user_email_tenant'),
    Index(
      'uq_single_owner_per_tenant',
      'tenant_id',
      unique=True,
      postgresql_where=(role == UserRole.OWNER)
    )
  )