"""
Pydantic schemas package for BillGuard API.
"""
from app.schemas.ai import (
    ReceiptLineItem,
    ReceiptParseResponse,
    BillItemInput,
    HistoricalBillInput,
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    BillSummaryInput,
    SubscriptionSummaryInput,
    CategoryBreakdown,
    MonthlyDigestRequest,
    MonthlyDigestResponse,
    AIStatusResponse,
)

__all__ = [
    "ReceiptLineItem",
    "ReceiptParseResponse",
    "BillItemInput",
    "HistoricalBillInput",
    "AnomalyDetectionRequest",
    "AnomalyDetectionResponse",
    "BillSummaryInput",
    "SubscriptionSummaryInput",
    "CategoryBreakdown",
    "MonthlyDigestRequest",
    "MonthlyDigestResponse",
    "AIStatusResponse",
]
