from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, String, func, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.domain.enums.cash_shift import CashShiftStatus

class CashShift(Base):
    __tablename__ = "cash_shifts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    opening_balance = Column(Numeric(10, 2), nullable=False)
    closing_balance = Column(Numeric(10, 2), nullable=True)
    expected_balance = Column(Numeric(10, 2), nullable=True)
    
    status = Column(Enum(CashShiftStatus), default=CashShiftStatus.OPEN, nullable=False)
    opened_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    observations = Column(String, nullable=True)

    user = relationship("User")