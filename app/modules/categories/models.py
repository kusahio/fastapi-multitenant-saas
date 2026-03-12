from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    discount = Column(Numeric(10, 2), default=0)
    is_discount_cumulative = Column(Boolean, default=False, nullable=False)
    is_discount_active = Column(Boolean, default=False, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    products = relationship("Product", back_populates="category")
