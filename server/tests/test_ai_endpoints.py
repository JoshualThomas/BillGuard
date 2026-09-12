"""
Integration tests for FastAPI AI endpoints.
Author: Joshual Thomas (AI & Intelligence Engineer)
"""
import io


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "BillGuard API"


def test_ai_status(client):
    """Test AI intelligence subsystem status endpoint."""
    response = client.get("/api/v1/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "BillGuard AI Engine"
    assert "supported_file_types" in data
    assert "status" in data


def test_parse_receipt_image(client):
    """Test multimodal receipt parsing with mock image data."""
    fake_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    files = {"file": ("electric_bill.png", io.BytesIO(fake_png), "image/png")}
    response = client.post("/api/v1/ai/parse-receipt", files=files, data={"currency_hint": "USD"})

    assert response.status_code == 200
    data = response.json()
    assert "vendor_name" in data
    assert "total_amount" in data
    assert data["total_amount"] > 0
    assert data["currency"] == "USD"
    assert "category" in data


def test_parse_receipt_invalid_file_type(client):
    """Test receipt parsing with unsupported file extension/MIME."""
    files = {"file": ("malicious.exe", io.BytesIO(b"executable data"), "application/x-dosexec")}
    response = client.post("/api/v1/ai/parse-receipt", files=files)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_detect_anomalies_baseline(client):
    """Test anomaly detection when no historical baseline exists."""
    payload = {
        "current_bill": {
            "vendor_name": "City Power",
            "category": "Electricity",
            "amount": 100.0,
            "billing_date": "2026-09-01",
            "currency": "USD",
            "is_subscription": False,
        },
        "historical_bills": [],
        "threshold_percent": 15.0,
    }
    response = client.post("/api/v1/ai/detect-anomalies", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_anomaly"] is False
    assert data["anomaly_type"] == "none"
    assert data["severity"] == "normal"


def test_detect_anomalies_price_spike(client):
    """Test price spike anomaly detection when bill surges > threshold."""
    payload = {
        "current_bill": {
            "vendor_name": "City Power",
            "category": "Electricity",
            "amount": 200.0,
            "billing_date": "2026-09-01",
            "currency": "USD",
            "is_subscription": False,
        },
        "historical_bills": [
            {"amount": 100.0, "billing_date": "2026-08-01"},
            {"amount": 105.0, "billing_date": "2026-07-01"},
            {"amount": 95.0, "billing_date": "2026-06-01"},
        ],
        "threshold_percent": 15.0,
        "include_ai_reasoning": False,
    }
    response = client.post("/api/v1/ai/detect-anomalies", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_anomaly"] is True
    assert data["anomaly_type"] == "price_spike"
    assert data["percentage_change"] >= 90.0
    assert "Electricity" in data["detailed_explanation"]


def test_detect_anomalies_subscription_hike(client):
    """Test subscription fee hike detection."""
    payload = {
        "current_bill": {
            "vendor_name": "StreamMax",
            "category": "Streaming & Entertainment",
            "amount": 19.99,
            "billing_date": "2026-09-01",
            "currency": "USD",
            "is_subscription": True,
        },
        "historical_bills": [
            {"amount": 14.99, "billing_date": "2026-08-01"},
            {"amount": 14.99, "billing_date": "2026-07-01"},
        ],
        "threshold_percent": 10.0,
        "include_ai_reasoning": False,
    }
    response = client.post("/api/v1/ai/detect-anomalies", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_anomaly"] is True
    assert data["anomaly_type"] == "subscription_hike"


def test_detect_anomalies_duplicate_charge(client):
    """Test duplicate billing detection on same billing date."""
    payload = {
        "current_bill": {
            "vendor_name": "Internet Co",
            "category": "Internet",
            "amount": 55.0,
            "billing_date": "2026-09-01",
            "currency": "USD",
            "is_subscription": True,
        },
        "historical_bills": [
            {"amount": 55.0, "billing_date": "2026-09-01"},
        ],
        "threshold_percent": 15.0,
        "include_ai_reasoning": False,
    }
    response = client.post("/api/v1/ai/detect-anomalies", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_anomaly"] is True
    assert data["anomaly_type"] == "duplicate_charge"
    assert data["severity"] == "critical"


def test_monthly_digest(client):
    """Test AI monthly financial digest generator with bills and zombie subscriptions."""
    payload = {
        "month": "2026-09",
        "bills": [
            {
                "vendor_name": "City Power",
                "category": "Electricity",
                "amount": 120.0,
                "due_date": "2026-09-18",
                "is_paid": False,
                "currency": "USD",
            },
            {
                "vendor_name": "Metro Water",
                "category": "Water",
                "amount": 45.0,
                "due_date": "2026-09-10",
                "is_paid": True,
                "currency": "USD",
            },
        ],
        "subscriptions": [
            {
                "service_name": "Cloud Storage",
                "category": "SaaS & Software",
                "cost": 9.99,
                "frequency": "monthly",
                "is_active": True,
            },
            {
                "service_name": "Unused Fitness App",
                "category": "Fitness",
                "cost": 29.99,
                "frequency": "monthly",
                "is_active": True,
                "last_used_days_ago": 60,
            },
        ],
        "monthly_budget": 250.0,
        "currency": "USD",
    }
    response = client.post("/api/v1/ai/monthly-digest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["period"] == "2026-09"
    assert data["total_spend"] == 204.98
    assert data["total_bills_count"] == 2
    assert data["total_subscriptions_count"] == 2
    assert data["unpaid_bills_amount"] == 120.0
    assert len(data["category_breakdown"]) > 0
    assert "markdown_report" in data
    assert "# 📊 BillGuard Monthly Financial Digest" in data["markdown_report"]
    # Verify zombie subscription alert
    assert any("Zombie Subscription Alert" in tip for tip in data["optimization_tips"])
