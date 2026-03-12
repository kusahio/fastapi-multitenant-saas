from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)

    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    products = relationship("Product", back_populates="category")
