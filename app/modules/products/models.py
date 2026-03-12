from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.domain.enums.unit_type import UnitType

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=False) 
    stock = Column(Numeric(10, 3), default=0) 
    unit_type = Column(Enum(UnitType), default=UnitType.UNIT, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    category = relationship("Category", back_populates="products")