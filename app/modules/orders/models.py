from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, Enum, String, func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.domain.enums.payment_type import PaymentType
from app.modules.cash_shifts.models import CashShift

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cash_shift_id = Column(Integer, ForeignKey("cash_shifts.id"), nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False, default=PaymentType.CASH)
    total = Column(Numeric(10, 2), nullable=False, default=0)   
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    tenant = relationship("Tenant")
    user = relationship("User")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_name = Column(String(100), nullable=False)
    quantity = Column(Numeric(10, 3), nullable=False) 
    unit_price = Column(Numeric(10, 2), nullable=False) 
    discount = Column(Numeric(10, 2), default=0)
    total_price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")