# 🛡️ BillGuard — Server & AI Intelligence Engine

This service powers the backend of **BillGuard**, including the **Google Gemini Multimodal AI Engine**, receipt & invoice parsing, smart anomaly & price-hike detection, and monthly financial digests.

---

## 👥 Module Ownership

- **AI & Intelligence Engineer**: **Joshual Thomas**
- **Primary Deliverables**:
  1. **Multimodal Receipt Parser Endpoint** (`POST /api/v1/ai/parse-receipt`)
  2. **Anomaly & Price-Hike Detection Algorithm** (`POST /api/v1/ai/detect-anomalies`)
  3. **AI Monthly Financial Digest Generator** (`POST /api/v1/ai/monthly-digest`)

---

## 🚀 Quickstart

### 1. Create and Activate Virtual Environment

```bash
cd server
python -m venv venv

# On Windows:
.\venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and set your `GEMINI_API_KEY` (from [Google AI Studio](https://aistudio.google.com/)). If omitted, the service will run in robust fallback mode.

### 4. Run Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

Interactive Swagger API docs will be available at: `http://localhost:8000/docs`.

---

## 📡 API Reference

### 1. Multimodal Receipt OCR
- **Endpoint**: `POST /api/v1/ai/parse-receipt`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: Image (JPEG, PNG, WEBP) or PDF invoice/receipt document.
  - `currency_hint` (optional): Default `USD` (e.g., `USD`, `INR`, `EUR`).
- **Response**:
  ```json
  {
    "vendor_name": "City Electric Utility",
    "invoice_number": "INV-2026-0812",
    "issue_date": "2026-09-01",
    "due_date": "2026-09-20",
    "billing_period": "Aug 2026 - Sep 2026",
    "subtotal": 112.32,
    "tax_amount": 12.48,
    "total_amount": 124.80,
    "currency": "USD",
    "category": "Electricity",
    "is_recurring": true,
    "suggested_frequency": "monthly",
    "confidence_score": 0.95,
    "parser_engine": "gemini (gemini-1.5-flash)"
  }
  ```

### 2. Anomaly & Price-Hike Detection
- **Endpoint**: `POST /api/v1/ai/detect-anomalies`
- **Payload**:
  ```json
  {
    "current_bill": {
      "vendor_name": "City Electric Utility",
      "category": "Electricity",
      "amount": 165.50,
      "billing_date": "2026-09-05",
      "currency": "USD",
      "is_subscription": false
    },
    "historical_bills": [
      { "amount": 110.00, "billing_date": "2026-08-05" },
      { "amount": 115.00, "billing_date": "2026-07-05" },
      { "amount": 105.00, "billing_date": "2026-06-05" }
    ],
    "threshold_percent": 15.0,
    "include_ai_reasoning": true
  }
  ```
- **Response**:
  ```json
  {
    "is_anomaly": true,
    "anomaly_type": "price_spike",
    "severity": "critical",
    "percentage_change": 50.45,
    "difference_amount": 55.50,
    "historical_average": 110.00,
    "historical_median": 110.00,
    "summary": "Anomaly detected: City Electric Utility bill of USD 165.5 is 50.45% above the historical average of USD 110.0.",
    "detailed_explanation": "Electricity usage spiked by 50.45% (+USD 55.50) over your historical baseline of USD 110.00.",
    "recommended_action": "Compare your kilowatt-hour (kWh) consumption on the bill against the previous month to isolate weather or tariff changes.",
    "analysis_engine": "heuristic-hybrid"
  }
  ```

### 3. AI Monthly Financial Digest
- **Endpoint**: `POST /api/v1/ai/monthly-digest`
- **Payload**:
  ```json
  {
    "month": "2026-09",
    "bills": [
      { "vendor_name": "Electric Utility", "category": "Electricity", "amount": 120.0, "due_date": "2026-09-20", "is_paid": false },
      { "vendor_name": "Metro Fiber", "category": "Internet", "amount": 60.0, "due_date": "2026-09-15", "is_paid": true }
    ],
    "subscriptions": [
      { "service_name": "Netflix", "category": "Streaming", "cost": 15.99, "frequency": "monthly", "is_active": true },
      { "service_name": "Gym Pass", "category": "Fitness", "cost": 45.00, "frequency": "monthly", "is_active": true, "last_used_days_ago": 45 }
    ],
    "monthly_budget": 300.0,
    "currency": "USD"
  }
  ```
- **Response**:
  Includes structured breakdown and a complete, formatted **Markdown financial report** with executive summary, category table, zombie subscription warnings, and savings tips.

---

## 🧪 Testing

Run test suite:

```bash
pytest tests/ -v
```

Linting:

```bash
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```
