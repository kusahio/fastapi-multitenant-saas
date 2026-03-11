from sqlalchemy import Column, String, Boolean, Integer, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Tenant(Base):
  __tablename__ = 'tenants'

  id = Column(Integer, primary_key=True)
  name = Column(String(100), nullable=False)
  slug = Column(String(50), unique=True, nullable=False)
  active = Column(Boolean, default=True)

  created_at = Column(
    DateTime(timezone=True),
    server_default=func.now()
  )

  user = relationship("UserTenant", back_populates="tenant", cascade="all, delete-orphan")