"""
Unit tests for GeminiAIService.
Author: Joshual Thomas (AI & Intelligence Engineer)
"""
import pytest
from app.services.gemini_service import GeminiAIService
from app.schemas.ai import (
    AnomalyDetectionRequest,
    BillItemInput,
    HistoricalBillInput,
    MonthlyDigestRequest,
    BillSummaryInput,
    SubscriptionSummaryInput,
)


@pytest.mark.asyncio
async def test_service_parse_receipt_fallback():
    """Verify heuristic fallback parsing works reliably when Gemini is unconfigured."""
    service = GeminiAIService()
    fake_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    result = await service.parse_receipt_multimodal(
        file_bytes=fake_png,
        filename="netflix_invoice.png",
        content_type="image/png",
        currency_hint="USD",
    )
    assert result.vendor_name == "Netflix"
    assert result.category == "Streaming & Entertainment"
    assert result.total_amount == 15.99
    assert result.is_recurring is True
    assert result.suggested_frequency == "monthly"


@pytest.mark.asyncio
async def test_service_detect_anomalies_rule_based():
    """Verify rule-based anomaly detection correctly flags spikes."""
    service = GeminiAIService()
    req = AnomalyDetectionRequest(
        current_bill=BillItemInput(
            vendor_name="Metro Gas",
            category="Gas",
            amount=150.0,
            billing_date="2026-09-01",
            currency="USD",
        ),
        historical_bills=[
            HistoricalBillInput(amount=80.0, billing_date="2026-08-01"),
            HistoricalBillInput(amount=85.0, billing_date="2026-07-01"),
        ],
        threshold_percent=20.0,
        include_ai_reasoning=False,
    )
    res = await service.detect_anomalies(req)
    assert res.is_anomaly is True
    assert res.anomaly_type == "price_spike"
    assert res.difference_amount > 0
    assert "Gas" in res.detailed_explanation


@pytest.mark.asyncio
async def test_service_generate_monthly_digest():
    """Verify digest calculation and markdown generation."""
    service = GeminiAIService()
    req = MonthlyDigestRequest(
        month="2026-09",
        bills=[
            BillSummaryInput(
                vendor_name="Electricity",
                category="Electricity",
                amount=100.0,
                due_date="2026-09-25",
                is_paid=False,
            )
        ],
        subscriptions=[
            SubscriptionSummaryInput(
                service_name="Music Streaming",
                category="Streaming",
                cost=10.0,
                is_active=True,
            )
        ],
        monthly_budget=200.0,
        currency="USD",
    )
    res = await service.generate_monthly_digest(req)
    assert res.total_spend == 110.0
    assert res.budget_used_percentage == 55.0
    assert len(res.category_breakdown) == 2
    assert "Electricity" in res.markdown_report
