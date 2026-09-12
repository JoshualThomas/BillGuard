from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class ReceiptLineItem(BaseModel):
    description: str
    amount: Decimal


class ReceiptParsedData(BaseModel):
    biller_name: str
    invoice_number: Optional[str] = None
    amount: Decimal = Field(..., decimal_places=2)
    currency: str = "USD"
    issue_date: Optional[str] = None
    due_date: Optional[str] = None
    billing_cycle: str = "MONTHLY"
    suggested_category: str = "Utilities"
    confidence_score: float = Field(default=0.9, ge=0.0, le=1.0)
    line_items: List[ReceiptLineItem] = []


class ReceiptParsedResponse(BaseModel):
    success: bool
    data: Optional[ReceiptParsedData] = None
    error: Optional[str] = None


class AnomalyAlertResponse(BaseModel):
    bill_id: Optional[str] = None
    biller_name: str
    current_amount: Decimal
    historical_average: Decimal
    percentage_increase: float
    severity: str  # LOW, MEDIUM, HIGH, NONE
    insight: str


class FinancialInsightResponse(BaseModel):
    monthly_outlook: str
    actionable_tips: List[str]
