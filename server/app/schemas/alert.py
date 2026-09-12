from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class AlertBase(BaseModel):
    alert_type: str  # DUE_DATE_REMINDER, PRICE_HIKE, UNUSUAL_EXPENSE, SUBSCRIPTION_RENEWAL
    title: str
    message: str
    channel: str = "IN_APP"  # EMAIL, TELEGRAM, IN_APP
    scheduled_for: datetime


class AlertCreate(AlertBase):
    user_id: UUID
    bill_id: Optional[UUID] = None
    subscription_id: Optional[UUID] = None


class AlertUpdate(BaseModel):
    status: Optional[str] = None  # PENDING, SENT, FAILED, READ


class AlertResponse(AlertBase):
    id: UUID
    user_id: UUID
    bill_id: Optional[UUID] = None
    subscription_id: Optional[UUID] = None
    status: str
    sent_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
