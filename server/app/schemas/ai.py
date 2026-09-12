"""
Pydantic Schemas for AI & Intelligence Services (Gemini OCR, Anomaly Detection, Monthly Digest).
Author: Joshual Thomas (AI & Intelligence Engineer)
"""
from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 1. Multimodal Receipt & Invoice OCR Schemas
# ---------------------------------------------------------------------------

class ReceiptLineItem(BaseModel):
    """Represents a single item extracted from a bill or receipt."""
    description: str = Field(..., description="Description or name of the item/charge")
    quantity: Optional[float] = Field(default=1.0, description="Quantity of the item")
    unit_price: Optional[float] = Field(default=None, description="Unit price per item")
    amount: Optional[float] = Field(default=None, description="Total amount for this line item")


class ReceiptParseResponse(BaseModel):
    """Structured response model for multimodal receipt parsing."""
    vendor_name: str = Field(..., description="Name of the billing company or merchant")
    invoice_number: Optional[str] = Field(default=None, description="Invoice, bill, or reference number")
    issue_date: Optional[str] = Field(default=None, description="Billing issue date in YYYY-MM-DD format")
    due_date: Optional[str] = Field(default=None, description="Payment due date in YYYY-MM-DD format")
    billing_period: Optional[str] = Field(default=None, description="Billing cycle or period (e.g., Aug 2026)")
    subtotal: Optional[float] = Field(default=None, description="Subtotal amount before taxes/fees")
    tax_amount: Optional[float] = Field(default=None, description="Extracted tax or surcharge amount")
    total_amount: float = Field(..., description="Total payable amount")
    currency: str = Field(default="USD", description="Currency symbol or 3-letter ISO code")
    category: str = Field(
        default="Other",
        description="Categorization e.g., Electricity, Water, Internet, Mobile Recharge, "
                    "Streaming & Entertainment, SaaS & Software, Insurance, Rent, Loan, Groceries, Other"
    )
    is_recurring: bool = Field(default=False, description="Whether this appears to be a recurring subscription/bill")
    suggested_frequency: Optional[str] = Field(
        default=None,
        description="Suggested recurrence frequency: monthly, quarterly, yearly, weekly, or one_time"
    )
    line_items: List[ReceiptLineItem] = Field(default_factory=list, description="Extracted itemized bill entries")
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0, description="Confidence score of AI extraction")
    notes: Optional[str] = Field(default=None, description="Any notable warnings, discounts, or terms extracted")
    parser_engine: str = Field(default="gemini-1.5-flash", description="Underlying AI model or engine used")


# ---------------------------------------------------------------------------
# 2. Smart Anomaly & Price-Hike Detection Schemas
# ---------------------------------------------------------------------------

class BillItemInput(BaseModel):
    """Input representation of the current bill being evaluated."""
    id: Optional[str] = Field(default=None, description="Unique identifier for the bill")
    vendor_name: str = Field(..., description="Vendor or provider name")
    category: str = Field(default="Utilities", description="Bill category")
    amount: float = Field(..., ge=0.0, description="Current bill amount")
    billing_date: str = Field(..., description="Billing date in YYYY-MM-DD format")
    currency: str = Field(default="USD", description="Currency code")
    is_subscription: bool = Field(default=False, description="Flag indicating if this is a recurring subscription")


class HistoricalBillInput(BaseModel):
    """Historical bill record for comparison."""
    amount: float = Field(..., ge=0.0, description="Past bill amount")
    billing_date: str = Field(..., description="Date of historical bill in YYYY-MM-DD format")
    vendor_name: Optional[str] = Field(default=None, description="Vendor name if applicable")
    notes: Optional[str] = Field(default=None, description="Optional notes or context for the historical bill")


class AnomalyDetectionRequest(BaseModel):
    """Request payload for anomaly and price-hike detection."""
    current_bill: BillItemInput
    historical_bills: List[HistoricalBillInput] = Field(
        default_factory=list,
        description="List of past bills from the same vendor or category for baseline comparison"
    )
    threshold_percent: float = Field(
        default=15.0,
        ge=1.0,
        le=200.0,
        description="Percentage surge considered anomalous (default 15%)"
    )
    include_ai_reasoning: bool = Field(
        default=True,
        description="Whether to run Gemini generative reasoning for contextual explanation"
    )


class AnomalyDetectionResponse(BaseModel):
    """Response payload detailing anomaly verdict, metrics, and guidance."""
    is_anomaly: bool = Field(..., description="True if an abnormal surge or discrepancy was detected")
    anomaly_type: str = Field(
        ...,
        description="Type of anomaly: price_spike, subscription_hike, duplicate_charge, unusual_frequency, or none"
    )
    severity: str = Field(
        ...,
        description="Severity level: normal, low, medium, high, or critical"
    )
    percentage_change: Optional[float] = Field(default=None, description="Percentage change compared to baseline")
    difference_amount: Optional[float] = Field(default=None, description="Absolute difference in bill amount")
    historical_average: Optional[float] = Field(default=None, description="Mean of historical comparison bills")
    historical_median: Optional[float] = Field(default=None, description="Median of historical comparison bills")
    summary: str = Field(..., description="Short summary of the analysis")
    detailed_explanation: str = Field(..., description="In-depth reasoning behind the verdict")
    recommended_action: str = Field(..., description="Actionable step for the user (e.g. audit usage, contact vendor)")
    analysis_engine: str = Field(default="gemini-1.5-flash", description="Engine used for reasoning")


# ---------------------------------------------------------------------------
# 3. AI Monthly Financial Digest Schemas
# ---------------------------------------------------------------------------

class BillSummaryInput(BaseModel):
    """Summary of a bill for digest calculation."""
    id: Optional[str] = None
    vendor_name: str
    category: str
    amount: float
    due_date: str
    is_paid: bool = False
    currency: str = "USD"


class SubscriptionSummaryInput(BaseModel):
    """Summary of an active subscription for digest calculation."""
    id: Optional[str] = None
    service_name: str
    category: str
    cost: float
    frequency: str = "monthly"
    next_billing_date: Optional[str] = None
    is_active: bool = True
    last_used_days_ago: Optional[int] = Field(
        default=None,
        description="Days since user last used this service (for zombie subscription detection)"
    )


class CategoryBreakdown(BaseModel):
    """Breakdown of spending per category."""
    category: str
    amount: float
    percentage: float


class MonthlyDigestRequest(BaseModel):
    """Request payload for generating a monthly financial intelligence report."""
    month: str = Field(..., description="Month identifier (e.g., '2026-09')")
    bills: List[BillSummaryInput] = Field(default_factory=list, description="Bills for the given month")
    subscriptions: List[SubscriptionSummaryInput] = Field(default_factory=list, description="Recurring subscriptions")
    monthly_budget: Optional[float] = Field(default=None, description="Optional target budget limit")
    currency: str = Field(default="USD", description="Currency symbol or ISO code")


class MonthlyDigestResponse(BaseModel):
    """Comprehensive AI-generated monthly financial digest."""
    period: str
    total_spend: float
    total_bills_count: int
    total_subscriptions_count: int
    active_subscriptions_cost: float
    unpaid_bills_amount: float
    category_breakdown: List[CategoryBreakdown]
    budget_used_percentage: Optional[float] = None
    executive_summary: str
    key_insights: List[str]
    optimization_tips: List[str]
    upcoming_obligations_summary: str
    markdown_report: str
    report_engine: str = "gemini-1.5-flash"


# ---------------------------------------------------------------------------
# 4. Service Health & Status Schemas
# ---------------------------------------------------------------------------

class AIStatusResponse(BaseModel):
    """Status report for the AI Intelligence subsystem."""
    service: str = "BillGuard AI Engine"
    gemini_configured: bool
    gemini_model: str
    supported_file_types: List[str]
    status: str
