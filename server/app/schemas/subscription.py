from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.category import CategoryResponse


class SubscriptionBase(BaseModel):
    service_name: str
    plan_name: Optional[str] = None
    cost: Decimal = Field(..., decimal_places=2)
    currency: str = "USD"
    billing_frequency: str = "MONTHLY"  # MONTHLY, YEARLY, QUARTERLY, WEEKLY
    next_renewal_date: date
    status: str = "ACTIVE"  # ACTIVE, PAUSED, CANCELLED
    trial_end_date: Optional[date] = None
    cancellation_url: Optional[str] = None


class SubscriptionCreate(SubscriptionBase):
    category_id: Optional[UUID] = None


class SubscriptionUpdate(BaseModel):
    service_name: Optional[str] = None
    plan_name: Optional[str] = None
    category_id: Optional[UUID] = None
    cost: Optional[Decimal] = None
    currency: Optional[str] = None
    billing_frequency: Optional[str] = None
    next_renewal_date: Optional[date] = None
    status: Optional[str] = None
    trial_end_date: Optional[date] = None
    cancellation_url: Optional[str] = None


class SubscriptionResponse(SubscriptionBase):
    id: UUID
    user_id: UUID
    category_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)
