from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.category import CategoryResponse


class BillBase(BaseModel):
    biller_name: str
    amount: Decimal = Field(..., decimal_places=2)
    currency: str = "USD"
    due_date: date
    billing_cycle: str = "MONTHLY"  # MONTHLY, QUARTERLY, ANNUALLY, ONE_TIME
    is_recurring: bool = True
    auto_pay: bool = False
    notes: Optional[str] = None
    receipt_url: Optional[str] = None


class BillCreate(BillBase):
    category_id: Optional[UUID] = None


class BillUpdate(BaseModel):
    biller_name: Optional[str] = None
    category_id: Optional[UUID] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    due_date: Optional[date] = None
    billing_cycle: Optional[str] = None
    status: Optional[str] = None
    is_recurring: Optional[bool] = None
    auto_pay: Optional[bool] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None


class BillResponse(BillBase):
    id: UUID
    user_id: UUID
    category_id: Optional[UUID] = None
    status: str
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)


class BillPaymentCreate(BaseModel):
    amount_paid: Decimal = Field(..., decimal_places=2)
    currency: str = "USD"
    payment_date: date = Field(default_factory=date.today)
    payment_method: str = "CREDIT_CARD"
    transaction_ref: Optional[str] = None
    notes: Optional[str] = None
