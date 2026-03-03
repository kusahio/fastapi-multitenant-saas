from sqlalchemy import Column, String, Boolean, Integer, Enum as SQLEnum, DateTime, func
from app.core.database import Base
from app.domain.enums.business_type import BusinessType

class Tenant(Base):
  __tablename__ = 'tenants'

  id = Column(Integer, primary_key=True)
  slug = Column(String(50), unique=True, nullable=False)
  name = Column(String(100), nullable=False)
  business_type = Column(
    SQLEnum(BusinessType, name='business_type_enum'), nullable=False
  )
  active = Column(Boolean, nullable=False ,server_default='false')
  created_at = Column(DateTime(timezone=True),nullable=False, server_default=func.now())

  def __repr__(self) -> str:
    return f'<Tenant id={self.id} slug="{self.slug}" active={self.active}>'