from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class CategorySpend(BaseModel):
    category_name: str
    icon: str
    color: str
    total_amount: Decimal
    percentage: float


class MonthlySpendTrend(BaseModel):
    month: str  # e.g., "Jan", "Feb"
    year: int
    bills_amount: Decimal
    subscriptions_amount: Decimal
    total: Decimal


class DashboardSummaryResponse(BaseModel):
    total_monthly_recurring: Decimal
    pending_bills_count: int
    pending_bills_total: Decimal
    active_subscriptions_count: int
    next_critical_due_date: Optional[date] = None
    category_breakdown: List[CategorySpend] = []
