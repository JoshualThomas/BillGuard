import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    telegram_chat_id = Column(String(100), nullable=True)
    email_notifications_enabled = Column(Boolean, default=True, nullable=False)
    telegram_notifications_enabled = Column(Boolean, default=False, nullable=False)

    # Relationships
    bills = relationship("Bill", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    payment_records = relationship("PaymentHistory", back_populates="user", cascade="all, delete-orphan")
