from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.domain.enums.tenant_role import TenantRole


class UserTenant(Base):
    __tablename__ = "user_tenants"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    role = Column(Enum(TenantRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "tenant_id", name="uq_user_tenant"),
    )

    user = relationship("User", back_populates="tenants")
    tenant = relationship("Tenant", back_populates="users")
