import pytest
from app.services.telegram_bot import TelegramBotService


def test_generate_upi_url():
    url = TelegramBotService.generate_upi_url(
        payee_vpa="bescom@sbi",
        payee_name="BESCOM Electricity",
        amount=1450.50,
        transaction_note="Oct Electricity"
    )
    assert url.startswith("upi://pay?")
    assert "pa=bescom%40sbi" in url
    assert "am=1450.50" in url
    assert "cu=INR" in url


@pytest.mark.anyio
async def test_mock_telegram_send():
    bill = {
        "id": "b-101",
        "vendor": "Airtel Broadband",
        "amount": 999.0,
        "currency_symbol": "₹",
        "due_date": "2026-10-15",
        "category": "Internet"
    }
    res = await TelegramBotService.send_bill_alert(
        chat_id="987654321",
        bill=bill,
        days_until_due=1,
        anomaly_warning="Plan increased by ₹150 vs last month"
    )
    assert res["status"] == "mock_delivered"
    assert res["chat_id"] == "987654321"
    assert "Airtel Broadband" in res["message"]
    assert "Anomaly Detected" in res["message"]


@pytest.mark.anyio
async def test_telegram_callback_handling():
    res = await TelegramBotService.handle_callback_query(
        callback_query_id="cq-123",
        callback_data="bill:paid:b-101",
        chat_id="987654321",
        message_id=456
    )
    assert res["status"] in ("success", "mock_handled")
    assert res["action"] == "paid"
    assert res["bill_id"] == "b-101"
