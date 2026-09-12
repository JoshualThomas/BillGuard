import uuid
from sqlalchemy import Column, String, Numeric, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    service_name = Column(String(150), nullable=False)
    plan_name = Column(String(100), nullable=True)
    cost = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    billing_frequency = Column(String(20), default="MONTHLY", nullable=False)  # MONTHLY, YEARLY, QUARTERLY, WEEKLY
    next_renewal_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, PAUSED, CANCELLED

    trial_end_date = Column(Date, nullable=True)
    cancellation_url = Column(String(500), nullable=True)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    category = relationship("Category", back_populates="subscriptions")
    alerts = relationship("Alert", back_populates="subscription", cascade="all, delete-orphan")
    payment_records = relationship("PaymentHistory", back_populates="subscription", cascade="all, delete-orphan")
