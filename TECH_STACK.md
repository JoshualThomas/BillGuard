# 🛠️ BillGuard — Technology Stack & Architectural Specifications

This document defines the complete technology stack, tools, versions, and architectural decisions adopted by the BillGuard engineering team.

---

## 1. Stack Architecture Overview

```
+-------------------------------------------------------------------------+
|                                CLIENT                                   |
|   Next.js 14+ (App Router) | TypeScript | Tailwind CSS | shadcn/ui      |
|   Lucide Icons | TanStack Query | Recharts | React Hook Form + Zod      |
+-------------------------------------------------------------------------+
                                    |
                            HTTP / REST API (JSON)
                                    |
                                    v
+-------------------------------------------------------------------------+
|                                SERVER                                   |
|   FastAPI (Python 3.11+) | Pydantic v2 | SQLAlchemy 2.0 | Uvicorn       |
|   JWT (python-jose, passlib) | Alembic (Migrations)                     |
+-------------------------------------------------------------------------+
         |                       |                        |
         v                       v                        v
+------------------+   +-------------------+    +--------------------+
|     DATABASE     |   |     AI ENGINE     |    |   NOTIFICATIONS    |
| PostgreSQL 16+   |   | Google Gemini     |    | Resend (Email)     |
| (Supabase/Neon)  |   | 1.5/2.0 Flash SDK |    | Telegram Bot API   |
+------------------+   +-------------------+    +--------------------+
                                 |
                                 v
                       +-------------------+
                       |    SCHEDULER      |
                       | APScheduler       |
                       | (Daily Crons)     |
                       +-------------------+
```

---

## 2. Layer-by-Layer Technology Breakdown

### 2.1 Frontend (Client)
- **Framework**: **Next.js 14+ (React 18/19, App Router)**
  - *Rationale*: Optimized performance via server components, nested routing for dashboards, built-in SEO capabilities, and rapid deployment on Vercel.
- **Language**: **TypeScript 5.x**
  - *Rationale*: Type-safe API responses, shared models with backend, and reduction of runtime bugs across team handoffs.
- **Styling & UI Library**: **Tailwind CSS + shadcn/ui**
  - *Rationale*: Accessible, copy-paste components built on Radix UI primitives; flexible styling without heavy runtime CSS-in-JS overhead.
- **Charts & Data Visualization**: **Recharts**
  - *Rationale*: Declarative, responsive charting for monthly spending forecasts, category breakdowns, and historical trends.
- **Form Handling & Validation**: **React Hook Form + Zod**
  - *Rationale*: Performant, un-opinionated form state with schema-driven validation matching backend Pydantic schemas.
- **Iconography**: **Lucide React**

---

### 2.2 Backend (Server)
- **Framework**: **FastAPI**
  - *Rationale*: High-throughput asynchronous Python framework, automatic OpenAPI (Swagger) documentation generation, and native integration with Python's AI/ML ecosystem.
- **Language**: **Python 3.11+**
  - *Rationale*: Native support for modern asynchronous programming (`async`/`await`), strong ecosystem for AI/LLM SDKs, image processing, and PDF extraction.
- **Data Validation & Serialisation**: **Pydantic v2**
  - *Rationale*: Ultra-fast C-extension based validation with clear schema serialization.
- **ORM & Migrations**: **SQLAlchemy 2.0 + Alembic**
  - *Rationale*: Robust relational abstraction layer, async database sessions, and repeatable versioned migration scripts.
- **Authentication**: **JWT (JSON Web Tokens) via `python-jose` + `passlib[bcrypt]`**
  - *Rationale*: Stateless, secure user session management with password hashing.
- **Background Scheduler**: **APScheduler (Advanced Python Scheduler)**
  - *Rationale*: Lightweight, in-process asynchronous cron scheduler to run automated daily scans for upcoming bills (7d, 3d, 1d triggers) without requiring heavy distributed infrastructure for MVP.

---

### 2.3 Database & Storage
- **Primary Database**: **PostgreSQL 15 / 16**
  - *Hosted Provider*: **Supabase** or **Neon** (or local PostgreSQL container).
  - *Rationale*: ACID compliance, structured schemas for financial ledgers, rich JSONB support for unstructured receipt metadata, and row-level security.
- **File / Document Storage**: **Local filesystem (dev) / Supabase Storage or AWS S3 (prod)**
  - *Rationale*: Secure binary storage for uploaded PDF bills and receipt images.

---

### 2.4 AI & Intelligent Data Processing
- **AI Model**: **Google Gemini 1.5 / 2.0 Flash**
  - *SDK*: `google-genai` / `google-generativeai`
  - *Capabilities*:
    1. **Multimodal Document Parsing**: Extraction of bill vendor, invoice number, issue date, due date, subtotal, taxes, total amount, and category from PDF/JPG/PNG.
    2. **Anomaly Detection**: Prompt-based heuristic analysis comparing current variable utility bills (electricity, water, mobile data) with historical trailing averages.
    3. **Actionable Financial Digest**: Generation of personalized, natural-language weekly summaries and subscription audit warnings.

---

### 2.5 Notifications & Third-Party Integrations
- **Email Service**: **Resend**
  - *Rationale*: Developer-friendly transactional email API with React-based email templates and high deliverability.
- **Instant Messaging Alerts**: **Telegram Bot API** (`python-telegram-bot` or HTTP Webhooks)
  - *Rationale*: Free, zero-setup, instant push notifications to users' phones without paying for SMS gateways (Twilio).
- **Calendar Synchronization**: **iCalendar (`.ics`) format**
  - *Rationale*: Native download/export compatible with Google Calendar, Apple Calendar, and Microsoft Outlook.

---

### 2.6 DevOps, Testing & Tooling
- **Containerization**: **Docker & Docker Compose** (for multi-service local development).
- **CI/CD**: **GitHub Actions**
  - Frontend: ESLint, Prettier, TypeScript compilation, Next.js build.
  - Backend: Flake8/Black, pytest test suite.
- **Hosting Targets**:
  - Frontend: **Vercel**
  - Backend: **Render** / **Railway**
  - Database: **Supabase** / **Neon**

---

## 3. Environment Variables Specification

Below are the required environment variables across the system:

### Backend (`server/.env`)
| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `PROJECT_NAME` | Name of the service | `BillGuard API` |
| `ENVIRONMENT` | Environment type | `development` / `production` |
| `SECRET_KEY` | Secret key for signing JWT tokens | `generate-a-secure-random-32-byte-key` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `1440` (24 hours) |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:password@localhost:5432/billguard` |
| `GEMINI_API_KEY` | Google AI Studio Gemini API Key | `AIzaSy...` |
| `RESEND_API_KEY` | Resend transactional email API key | `re_123...` |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token from BotFather | `123456789:ABCdef...` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000` |

### Frontend (`client/.env.local`)
| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | Base URL for FastAPI backend | `http://localhost:8000` |
| `NEXT_PUBLIC_APP_NAME` | Application title | `BillGuard` |

---

## 4. Key Architectural Decisions (ADR Summary)

1. **Why FastAPI instead of Express/Node for Backend?**
   - Direct compatibility with Google Gemini Python SDK and image/PDF processing libraries (`Pillow`, `pypdf`).
   - Built-in data validation with Pydantic and auto-generated Swagger UI for fast client-backend synchronization.
2. **Why Gemini Flash over Gemini Pro / OpenAI GPT-4o?**
   - Gemini Flash delivers sub-second response times and multimodal capabilities at a fraction of the cost, making it ideal for real-time document OCR and rapid batch analysis.
3. **Why Telegram Bot for MVP Notifications?**
   - SMS services require business entity verification, DLT registration, and per-SMS fees. A Telegram bot provides instant mobile push notifications for free during hackathons and student projects.
