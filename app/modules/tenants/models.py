from sqlalchemy import Column, String, Boolean, Integer, DateTime, func, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.domain.enums.business_type import BusinessType

class Tenant(Base):
  __tablename__ = 'tenants'

  id = Column(Integer, primary_key=True)
  name = Column(String(100), nullable=False)
  slug = Column(String(50), unique=True, nullable=False)
  business_type = Column(Enum(BusinessType), nullable=False)
  active = Column(Boolean, default=True)

  created_at = Column(
    DateTime(timezone=True),
    server_default=func.now()
  )

  users = relationship("UserTenant", back_populates="tenant", cascade="all, delete-orphan")