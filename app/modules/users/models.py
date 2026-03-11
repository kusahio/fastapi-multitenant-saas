from sqlalchemy import Column, String, Boolean, Integer, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    is_platform_admin = Column(Boolean, default=False, nullable=False)

    created_at = Column(
        DateTime(timezone=True), 
        nullable=False,
        server_default=func.now()
    )
    
    tenants = relationship("UserTenant", back_populates="user", cascade="all, delete-orphan")