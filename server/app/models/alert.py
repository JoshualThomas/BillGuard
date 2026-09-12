import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import generate_uuid


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id", ondelete="CASCADE"), nullable=True)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=True)

    alert_type = Column(String(50), nullable=False)  # DUE_DATE_REMINDER, PRICE_HIKE, UNUSUAL_EXPENSE, SUBSCRIPTION_RENEWAL
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    channel = Column(String(20), default="IN_APP", nullable=False)  # EMAIL, TELEGRAM, IN_APP
    status = Column(String(20), default="PENDING", nullable=False, index=True)  # PENDING, SENT, FAILED, READ

    scheduled_for = Column(DateTime(timezone=True), nullable=False, index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="alerts")
    bill = relationship("Bill", back_populates="alerts")
    subscription = relationship("Subscription", back_populates="alerts")
