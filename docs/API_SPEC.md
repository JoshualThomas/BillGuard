# 📡 BillGuard REST API Specification (OpenAPI Contract)

Base URL: `http://localhost:8000/api/v1`  
Content-Type: `application/json`  
Authentication: `Bearer <JWT_TOKEN>` (Header: `Authorization: Bearer <token>`)

---

## 1. Authentication & Users (`/auth`)

### 1.1 `POST /auth/register`
Create a new user account.
- **Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "Jane Doe",
  "currency": "USD"
}
```
- **Response (201 Created)**:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "currency": "USD",
  "created_at": "2026-09-12T10:00:00Z"
}
```

### 1.2 `POST /auth/login`
Authenticate and obtain JWT access token.
- **Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```
- **Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "email": "user@example.com",
    "full_name": "Jane Doe"
  }
}
```

### 1.3 `GET /auth/me`
Retrieve profile of currently authenticated user.
- **Response (200 OK)**: Returns user object and notification preferences.

---

## 2. Bills Management (`/bills`)

### 2.1 `GET /bills`
List bills for authenticated user with query filters.
- **Query Parameters**:
  - `status`: `PENDING` | `PAID` | `OVERDUE` (optional)
  - `category_id`: UUID (optional)
  - `start_date`: `YYYY-MM-DD` (optional)
  - `end_date`: `YYYY-MM-DD` (optional)
- **Response (200 OK)**:
```json
[
  {
    "id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
    "biller_name": "Pacific Gas & Electric",
    "amount": 142.50,
    "currency": "USD",
    "due_date": "2026-09-28",
    "billing_cycle": "MONTHLY",
    "status": "PENDING",
    "is_recurring": true,
    "auto_pay": false,
    "category": {
      "id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
      "name": "Utilities",
      "icon": "zap",
      "color": "#F59E0B"
    }
  }
]
```

### 2.2 `POST /bills`
Create a new bill manually.
- **Request Body**:
```json
{
  "biller_name": "Electricity Board",
  "category_id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
  "amount": 85.00,
  "currency": "USD",
  "due_date": "2026-10-05",
  "billing_cycle": "MONTHLY",
  "is_recurring": true,
  "auto_pay": false,
  "notes": "Expected hike for AC usage"
}
```
- **Response (201 Created)**: Returns created bill record.

### 2.3 `POST /bills/{id}/pay`
Mark bill as paid and log into payment history.
- **Request Body**:
```json
{
  "payment_date": "2026-09-28",
  "payment_method": "CREDIT_CARD",
  "transaction_ref": "TXN_987654321",
  "amount_paid": 85.00
}
```
- **Response (200 OK)**: Bill status updated to `PAID`.

---

## 3. Subscriptions Management (`/subscriptions`)

### 3.1 `GET /subscriptions`
List all active and paused recurring subscriptions.
- **Response (200 OK)**:
```json
[
  {
    "id": "6fa85f64-5717-4562-b3fc-2c963f66afa9",
    "service_name": "Netflix",
    "plan_name": "Premium 4K",
    "cost": 22.99,
    "currency": "USD",
    "billing_frequency": "MONTHLY",
    "next_renewal_date": "2026-10-01",
    "status": "ACTIVE",
    "cancellation_url": "https://netflix.com/cancel"
  }
]
```

### 3.2 `POST /subscriptions`
Register a new subscription.

---

## 4. AI & Intelligence Endpoints (`/ai`)

### 4.1 `POST /ai/parse-receipt`
Uploads a document (PDF / JPG / PNG) to be parsed by **Google Gemini Flash**.
- **Content-Type**: `multipart/form-data`
- **Form Field**: `file` (binary)
- **Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "biller_name": "Verizon Wireless",
    "invoice_number": "INV-2026-902",
    "amount": 79.99,
    "currency": "USD",
    "issue_date": "2026-09-10",
    "due_date": "2026-09-25",
    "billing_cycle": "MONTHLY",
    "suggested_category": "Mobile & Internet",
    "confidence_score": 0.96,
    "line_items": [
      { "description": "Unlimited 5G Plan", "amount": 75.00 },
      { "description": "Regulatory Fee", "amount": 4.99 }
    ]
  }
}
```

### 4.2 `GET /ai/anomalies`
Evaluates user's bill history for price hikes and anomalies.
- **Response (200 OK)**:
```json
[
  {
    "bill_id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
    "biller_name": "Pacific Gas & Electric",
    "current_amount": 142.50,
    "historical_average": 95.00,
    "percentage_increase": 50.0,
    "severity": "HIGH",
    "insight": "Electricity bill is 50% higher than your 3-month average ($95.00)."
  }
]
```

### 4.3 `GET /ai/insights`
Generates natural-language financial guardian advice.
- **Response (200 OK)**:
```json
{
  "monthly_outlook": "You have $485.50 in upcoming recurring commitments before month end.",
  "actionable_tips": [
    "You have not logged usage on 'Adobe Creative Cloud' for 60 days ($54.99/mo). Consider pausing.",
    "Your mobile plan renewed at an increased rate of $79.99 (+10%). Check carrier options."
  ]
}
```

---

## 5. Analytics & Dashboard Summary (`/analytics`)

### 5.1 `GET /analytics/summary`
Returns KPI metrics for the user dashboard.
- **Response (200 OK)**:
```json
{
  "total_monthly_recurring": 642.50,
  "pending_bills_count": 3,
  "pending_bills_total": 307.49,
  "active_subscriptions_count": 5,
  "next_critical_due_date": "2026-09-25",
  "category_breakdown": [
    { "category_name": "Utilities", "total": 237.50, "percentage": 37.0 },
    { "category_name": "Subscriptions", "total": 95.00, "percentage": 14.8 }
  ]
}
```

---

## 6. Alerts & Notifications (`/alerts`)

### 6.1 `GET /alerts`
Fetch user alerts.
### 6.2 `PATCH /alerts/{id}/read`
Mark alert as read.
