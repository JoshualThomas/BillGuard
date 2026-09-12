from datetime import date
from decimal import Decimal
import uuid
import pytest
from pydantic import ValidationError

from app.schemas.bill import BillCreate, BillResponse
from app.schemas.subscription import SubscriptionCreate
from app.schemas.user import UserCreate
from app.schemas.ai import ReceiptParsedData


def test_user_create_validation():
    user = UserCreate(
        email="test@example.com",
        password="secretpassword",
        full_name="Alex Mercer",
        currency="USD",
    )
    assert user.email == "test@example.com"
    assert user.currency == "USD"


def test_bill_create_validation():
    bill = BillCreate(
        biller_name="Pacific Electric",
        amount=Decimal("124.50"),
        currency="USD",
        due_date=date(2026, 10, 15),
        billing_cycle="MONTHLY",
        is_recurring=True,
    )
    assert bill.amount == Decimal("124.50")
    assert bill.biller_name == "Pacific Electric"


def test_subscription_create_validation():
    sub = SubscriptionCreate(
        service_name="Spotify",
        plan_name="Premium Duo",
        cost=Decimal("14.99"),
        billing_frequency="MONTHLY",
        next_renewal_date=date(2026, 10, 1),
    )
    assert sub.service_name == "Spotify"
    assert sub.cost == Decimal("14.99")


def test_ai_receipt_parsed_data():
    receipt = ReceiptParsedData(
        biller_name="Costco Wholesale",
        amount=Decimal("245.12"),
        suggested_category="Groceries & Supplies",
        confidence_score=0.98,
        line_items=[
            {"description": "Paper Towels", "amount": Decimal("22.50")}
        ]
    )
    assert receipt.confidence_score == 0.98
    assert len(receipt.line_items) == 1
