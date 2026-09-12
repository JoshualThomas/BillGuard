import uuid
from sqlalchemy import Column, String, Numeric, Date, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class Bill(Base, TimestampMixin):
    __tablename__ = "bills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    biller_name = Column(String(150), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    billing_cycle = Column(String(20), default="MONTHLY", nullable=False)  # MONTHLY, QUARTERLY, ANNUALLY, ONE_TIME
    status = Column(String(20), default="PENDING", nullable=False, index=True)  # PENDING, PAID, OVERDUE

    is_recurring = Column(Boolean, default=True, nullable=False)
    auto_pay = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
    receipt_url = Column(String(500), nullable=True)

    # Relationships
    user = relationship("User", back_populates="bills")
    category = relationship("Category", back_populates="bills")
    alerts = relationship("Alert", back_populates="bill", cascade="all, delete-orphan")
    payment_records = relationship("PaymentHistory", back_populates="bill", cascade="all, delete-orphan")
