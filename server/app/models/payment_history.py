import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, Date, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import generate_uuid


class PaymentHistory(Base):
    __tablename__ = "payment_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id", ondelete="SET NULL"), nullable=True)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True)

    amount_paid = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    payment_date = Column(Date, nullable=False, index=True)
    payment_method = Column(String(50), default="CREDIT_CARD", nullable=False)  # CREDIT_CARD, BANK_TRANSFER, UPI, CASH
    transaction_ref = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="payment_records")
    bill = relationship("Bill", back_populates="payment_records")
    subscription = relationship("Subscription", back_populates="payment_records")
