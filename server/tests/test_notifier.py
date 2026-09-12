import pytest
from app.services.notifier import NotificationDispatcher, NotificationPriority, NotificationChannel
from app.services.email_service import EmailService


@pytest.mark.anyio
async def test_email_service_mock_delivery_and_ics():
    bill = {
        "id": "b-202",
        "vendor": "Netflix 4K",
        "amount": 649.0,
        "currency_symbol": "₹",
        "due_date": "2026-10-20",
        "category": "Entertainment"
    }
    res = await EmailService.send_bill_reminder(
        user_email="alex@example.com",
        bill=bill,
        days_until_due=3
    )
    assert res["status"] == "mock_delivered"
    assert res["to"] == "alex@example.com"
    assert "Netflix 4K" in res["subject"]
    assert "token=" in res["magic_mark_paid_url"]


@pytest.mark.anyio
async def test_notifier_multi_channel_dispatch():
    user = {
        "email": "sarah@example.com",
        "telegram_chat_id": "11223344"
    }
    bill = {
        "id": "b-303",
        "vendor": "BESCOM Electricity",
        "amount": 1820.0,
        "currency_symbol": "₹",
        "due_date": "2026-10-05",
        "category": "Electricity"
    }
    
    # Urgent alert (due in 1 day with anomaly)
    res = await NotificationDispatcher.dispatch_bill_reminder(
        user=user,
        bill=bill,
        days_until_due=1,
        anomaly_warning="Spike of 35% in electricity units detected",
        preferred_channel=NotificationChannel.ALL
    )
    
    assert res["priority"] == NotificationPriority.URGENT.value
    assert "telegram" in res["channels_attempted"]
    assert "email" in res["channels_attempted"]
    assert res["deliveries"]["telegram"]["status"] == "mock_delivered"
    assert res["deliveries"]["email"]["status"] == "mock_delivered"
