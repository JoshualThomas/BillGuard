"""
Gemini AI Intelligence Service: Multimodal Document Parsing, Anomaly Detection & Financial Digests.
Author: Joshual Thomas (AI & Intelligence Engineer)
"""
import io
import json
import logging
import statistics
from typing import Dict, List, Optional

from app.core.config import settings
from app.schemas.ai import (
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    CategoryBreakdown,
    MonthlyDigestRequest,
    MonthlyDigestResponse,
    ReceiptLineItem,
    ReceiptParseResponse,
)

logger = logging.getLogger("billguard.ai_service")

# Try importing google-generativeai; if missing or unconfigured, fallback gracefully
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    pypdf = None
    PYPDF_AVAILABLE = False


class GeminiAIService:
    """Core AI Service handling Multimodal OCR, Heuristic/Generative Anomaly Detection,

    and Monthly Financial Digest Generation.
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL or "gemini-1.5-flash"
        self._is_initialized = False

        if GENAI_AVAILABLE and self.api_key and not self.api_key.startswith("your-"):
            try:
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self.model_name)
                self._is_initialized = True
                logger.info("Google Gemini client initialized successfully with model %s", self.model_name)
            except Exception as e:
                logger.warning("Failed to configure Gemini client: %s. Using heuristic fallback.", e)
                self._is_initialized = False
        else:
            logger.info("Gemini API key not configured or placeholder detected. Operating in mock/heuristic mode.")

    @property
    def is_configured(self) -> bool:
        """Returns True if Google Gemini API is live and configured."""
        return self._is_initialized

    # -------------------------------------------------------------------------
    # 1. Multimodal Receipt & Invoice Parsing
    # -------------------------------------------------------------------------
    async def parse_receipt_multimodal(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        currency_hint: str = "USD",
    ) -> ReceiptParseResponse:
        """Parses an invoice or receipt image/PDF and extracts structured billing data."""
        # Check if PDF and extract text if applicable
        extracted_text = ""
        if (content_type == "application/pdf" or filename.lower().endswith(".pdf")) and PYPDF_AVAILABLE:
            try:
                pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += page_text + "\n"
            except Exception as e:
                logger.warning("Failed extracting text from PDF with pypdf: %s", e)

        if self._is_initialized:
            try:
                return await self._parse_with_gemini(
                    file_bytes=file_bytes,
                    content_type=content_type,
                    pdf_text=extracted_text,
                    currency_hint=currency_hint,
                )
            except Exception as e:
                logger.error("Gemini OCR parsing failed with error: %s. Falling back to heuristic extractor.", e)

        # Fallback heuristic parser
        return self._heuristic_receipt_parser(
            filename=filename,
            extracted_text=extracted_text,
            currency_hint=currency_hint,
        )

    async def _parse_with_gemini(
        self,
        file_bytes: bytes,
        content_type: str,
        pdf_text: str,
        currency_hint: str,
    ) -> ReceiptParseResponse:
        """Invokes Gemini Multimodal model with strict JSON schema instructions."""
        prompt = (
            "You are an expert financial auditor and receipt/invoice parser. "
            "Extract the following information from the provided document into valid, strict JSON ONLY. "
            "Do not include any conversational preamble or markdown code fence wrappers (or use standard "
            "```json ... ```).\n\n"
            "JSON structure required:\n"
            "{\n"
            '  "vendor_name": string (merchant/vendor name),\n'
            '  "invoice_number": string or null,\n'
            '  "issue_date": string (YYYY-MM-DD or null),\n'
            '  "due_date": string (YYYY-MM-DD or null),\n'
            '  "billing_period": string or null,\n'
            '  "subtotal": float or null,\n'
            '  "tax_amount": float or null,\n'
            '  "total_amount": float (total payable),\n'
            f'  "currency": string (e.g. "{currency_hint}"),\n'
            '  "category": string (one of: Electricity, Water, Internet, Mobile Recharge, '
            'Streaming & Entertainment, SaaS & Software, Insurance, Rent & Housing, Loan / EMI, Groceries, Other),\n'
            '  "is_recurring": boolean,\n'
            '  "suggested_frequency": string or null (monthly, quarterly, yearly, weekly, one_time),\n'
            '  "line_items": [\n'
            '     {"description": string, "quantity": float, "unit_price": float or null, "amount": float}\n'
            '  ],\n'
            '  "confidence_score": float (0.0 to 1.0),\n'
            '  "notes": string or null\n'
            "}"
        )

        content_parts = [prompt]
        if pdf_text:
            content_parts.append(f"Document Extracted Text:\n{pdf_text[:4000]}")

        # Add image/document blob if image
        if content_type.startswith("image/"):
            content_parts.append({"mime_type": content_type, "data": file_bytes})
        elif content_type == "application/pdf":
            content_parts.append({"mime_type": "application/pdf", "data": file_bytes})

        response = self._model.generate_content(content_parts)
        text_resp = response.text.strip()

        # Clean JSON markdown if present
        if text_resp.startswith("```json"):
            text_resp = text_resp[7:]
        elif text_resp.startswith("```"):
            text_resp = text_resp[3:]
        if text_resp.endswith("```"):
            text_resp = text_resp[:-3]
        text_resp = text_resp.strip()

        data = json.loads(text_resp)
        data["parser_engine"] = f"gemini ({self.model_name})"
        return ReceiptParseResponse(**data)

    def _heuristic_receipt_parser(
        self,
        filename: str,
        extracted_text: str,
        currency_hint: str,
    ) -> ReceiptParseResponse:
        """Deterministic heuristic fallback when Gemini API is offline or key is unset."""
        fn_lower = filename.lower()
        text_lower = extracted_text.lower()

        # Vendor inference
        vendor = "Unknown Merchant"
        category = "Other"
        is_recurring = False
        frequency = "one_time"

        if "electric" in fn_lower or "power" in fn_lower or "electric" in text_lower:
            vendor = "City Electric Utility"
            category = "Electricity"
            is_recurring = True
            frequency = "monthly"
        elif "water" in fn_lower or "water" in text_lower:
            vendor = "Municipal Water Board"
            category = "Water"
            is_recurring = True
            frequency = "monthly"
        elif "internet" in fn_lower or "wifi" in fn_lower or "broadband" in text_lower:
            vendor = "Metro Fiber Internet"
            category = "Internet"
            is_recurring = True
            frequency = "monthly"
        elif "netflix" in fn_lower or "netflix" in text_lower:
            vendor = "Netflix"
            category = "Streaming & Entertainment"
            is_recurring = True
            frequency = "monthly"
        elif "spotify" in fn_lower or "spotify" in text_lower:
            vendor = "Spotify"
            category = "Streaming & Entertainment"
            is_recurring = True
            frequency = "monthly"
        elif "aws" in fn_lower or "amazon web services" in text_lower:
            vendor = "Amazon Web Services"
            category = "SaaS & Software"
            is_recurring = True
            frequency = "monthly"
        elif "airtel" in fn_lower or "verizon" in fn_lower or "mobile" in text_lower:
            vendor = "Telecom Mobile Services"
            category = "Mobile Recharge"
            is_recurring = True
            frequency = "monthly"

        # Amount heuristic
        total_amount = 75.50
        if "netflix" in vendor.lower():
            total_amount = 15.99
        elif "spotify" in vendor.lower():
            total_amount = 10.99
        elif category == "Electricity":
            total_amount = 124.80

        return ReceiptParseResponse(
            vendor_name=vendor,
            invoice_number=f"INV-2026-{abs(hash(filename)) % 10000:04d}",
            issue_date="2026-09-01",
            due_date="2026-09-20",
            billing_period="Aug 2026 - Sep 2026",
            subtotal=round(total_amount * 0.9, 2),
            tax_amount=round(total_amount * 0.1, 2),
            total_amount=total_amount,
            currency=currency_hint,
            category=category,
            is_recurring=is_recurring,
            suggested_frequency=frequency,
            line_items=[
                ReceiptLineItem(
                    description=f"{category} standard billing cycle",
                    quantity=1.0,
                    unit_price=round(total_amount * 0.9, 2),
                    amount=round(total_amount * 0.9, 2),
                )
            ],
            confidence_score=0.85,
            notes="Processed via local heuristic engine (Configure GEMINI_API_KEY for live multimodal vision extraction).",
            parser_engine="local-heuristic-engine",
        )

    # -------------------------------------------------------------------------
    # 2. Smart Anomaly & Price-Hike Detection Algorithm
    # -------------------------------------------------------------------------
    async def detect_anomalies(self, request: AnomalyDetectionRequest) -> AnomalyDetectionResponse:
        """Analyzes a bill against historical records using statistical heuristics

        and Gemini generative financial reasoning.
        """
        curr = request.current_bill
        hist = request.historical_bills
        threshold = request.threshold_percent

        if not hist:
            return AnomalyDetectionResponse(
                is_anomaly=False,
                anomaly_type="none",
                severity="normal",
                percentage_change=0.0,
                difference_amount=0.0,
                historical_average=curr.amount,
                historical_median=curr.amount,
                summary=f"First recorded bill for {curr.vendor_name}.",
                detailed_explanation="No prior bills found for baseline comparison. Recorded as reference baseline.",
                recommended_action="Continue recording bills to build an accurate baseline for anomaly detection.",
                analysis_engine="heuristic-baseline",
            )

        amounts = [h.amount for h in hist]
        avg_amount = round(statistics.mean(amounts), 2)
        median_amount = round(statistics.median(amounts), 2)
        diff_amount = round(curr.amount - avg_amount, 2)
        pct_change = round(((curr.amount - avg_amount) / avg_amount) * 100, 2) if avg_amount > 0 else 0.0

        is_anomaly = False
        anomaly_type = "none"
        severity = "normal"

        # Check 1: Duplicate charge detection
        for past_bill in hist:
            if abs(past_bill.amount - curr.amount) < 0.01 and past_bill.billing_date == curr.billing_date:
                is_anomaly = True
                anomaly_type = "duplicate_charge"
                severity = "critical"
                break

        # Check 2: Subscription price hike detection
        if not is_anomaly and curr.is_subscription:
            last_bill = sorted(hist, key=lambda x: x.billing_date, reverse=True)[0]
            if curr.amount > last_bill.amount:
                is_anomaly = True
                anomaly_type = "subscription_hike"
                hike_pct = round(((curr.amount - last_bill.amount) / last_bill.amount) * 100, 2)
                severity = "high" if hike_pct >= 20.0 else "medium"

        # Check 3: Variable utility price spike detection
        if not is_anomaly and pct_change >= threshold:
            is_anomaly = True
            anomaly_type = "price_spike"
            if pct_change >= 50.0:
                severity = "critical"
            elif pct_change >= 25.0:
                severity = "high"
            else:
                severity = "medium"
        elif not is_anomaly and pct_change <= -threshold:
            # Significant drop
            anomaly_type = "unusual_drop"
            severity = "low"

        # Generate Contextual Summary & Detailed Guidance
        summary = (
            f"Anomaly detected: {curr.vendor_name} bill of {curr.currency} {curr.amount} "
            f"is {pct_change}% {'above' if pct_change > 0 else 'below'} the historical average "
            f"of {curr.currency} {avg_amount}."
            if is_anomaly
            else f"{curr.vendor_name} bill of {curr.currency} {curr.amount} is within normal expected variance."
        )

        detailed_explanation = ""
        recommended_action = ""

        # Use Gemini Generative reasoning if configured and requested
        if self._is_initialized and request.include_ai_reasoning and is_anomaly:
            try:
                ai_reasoning = await self._generate_anomaly_reasoning(
                    curr=curr,
                    avg=avg_amount,
                    diff=diff_amount,
                    pct=pct_change,
                    anomaly_type=anomaly_type,
                    severity=severity,
                )
                detailed_explanation = ai_reasoning.get("explanation", "")
                recommended_action = ai_reasoning.get("action", "")
            except Exception as e:
                logger.warning("Gemini anomaly reasoning failed: %s. Using rule-based guidance.", e)

        # Fallback deterministic reasoning
        if not detailed_explanation:
            detailed_explanation, recommended_action = self._rule_based_anomaly_guidance(
                curr=curr,
                anomaly_type=anomaly_type,
                pct_change=pct_change,
                diff_amount=diff_amount,
                avg_amount=avg_amount,
            )

        return AnomalyDetectionResponse(
            is_anomaly=is_anomaly,
            anomaly_type=anomaly_type,
            severity=severity,
            percentage_change=pct_change,
            difference_amount=diff_amount,
            historical_average=avg_amount,
            historical_median=median_amount,
            summary=summary,
            detailed_explanation=detailed_explanation,
            recommended_action=recommended_action,
            analysis_engine=f"gemini ({self.model_name})" if (self._is_initialized and is_anomaly) else "heuristic-hybrid",
        )

    async def _generate_anomaly_reasoning(
        self,
        curr,
        avg: float,
        diff: float,
        pct: float,
        anomaly_type: str,
        severity: str,
    ) -> Dict[str, str]:
        """Prompts Gemini to generate natural-language financial analysis for an anomaly."""
        prompt = (
            f"You are an AI financial auditor. An anomaly was detected in a user's expenses:\n"
            f"- Vendor: {curr.vendor_name}\n"
            f"- Category: {curr.category}\n"
            f"- Current Amount: {curr.currency} {curr.amount} on {curr.billing_date}\n"
            f"- Historical Trailing Average: {curr.currency} {avg}\n"
            f"- Surge: {pct}% ({curr.currency} {diff})\n"
            f"- Anomaly Type: {anomaly_type}\n"
            f"- Severity: {severity}\n\n"
            f"Provide a concise JSON response with exactly two keys:\n"
            f'1. "explanation": 2 sentences explaining why this anomaly occurred based on the category '
            f'(e.g., utility rate hike, seasonal HVAC, unnotified subscription increase).\n'
            f'2. "action": 1-2 concrete, practical steps the user should take right now.\n'
            f"JSON ONLY:"
        )
        response = self._model.generate_content(prompt)
        text_resp = response.text.strip()
        if text_resp.startswith("```json"):
            text_resp = text_resp[7:]
        if text_resp.startswith("```"):
            text_resp = text_resp[3:]
        if text_resp.endswith("```"):
            text_resp = text_resp[:-3]
        return json.loads(text_resp.strip())

    def _rule_based_anomaly_guidance(
        self,
        curr,
        anomaly_type: str,
        pct_change: float,
        diff_amount: float,
        avg_amount: float,
    ) -> tuple[str, str]:
        """Provides deterministic explanations when AI reasoning is unavailable."""
        if anomaly_type == "duplicate_charge":
            return (
                f"A duplicate billing entry of {curr.currency} {curr.amount} was detected for {curr.vendor_name} "
                f"with an identical transaction date.",
                "Verify your bank/card statement. If charged twice, contact the vendor support team to request a refund."
            )
        elif anomaly_type == "subscription_hike":
            return (
                f"{curr.vendor_name} increased your recurring subscription fee by {pct_change}% "
                f"(+{curr.currency} {diff_amount}).",
                "Review the new plan terms. Check if promotional pricing expired or if an annual plan offers a discount."
            )
        elif anomaly_type == "price_spike":
            if curr.category.lower() == "electricity":
                return (
                    f"Electricity usage spiked by {pct_change}% (+{curr.currency} {diff_amount}) "
                    f"over your historical baseline of {curr.currency} {avg_amount}.",
                    "Compare your kilowatt-hour (kWh) consumption on the bill against the previous month to isolate weather or tariff changes."
                )
            elif curr.category.lower() in ["water", "gas"]:
                return (
                    f"{curr.category} bill surged by {pct_change}% above the trailing average.",
                    "Inspect plumbing fixtures for unnoticed leaks or check the meter reading against the invoice."
                )
            else:
                return (
                    f"Unusual surge of {pct_change}% (+{curr.currency} {diff_amount}) detected for {curr.vendor_name}.",
                    "Check the itemized invoice breakdown for unexpected one-off surcharges, taxes, or rate changes."
                )
        else:
            return (
                f"Bill amount is consistent with your past average of {curr.currency} {avg_amount}.",
                "No action required. Bill is within normal historical tolerances."
            )

    # -------------------------------------------------------------------------
    # 3. AI Monthly Financial Digest Generator
    # -------------------------------------------------------------------------
    async def generate_monthly_digest(self, request: MonthlyDigestRequest) -> MonthlyDigestResponse:
        """Compiles monthly bills and subscriptions into an insightful, executive summary

        with category distribution and actionable optimization recommendations.
        """
        month = request.month
        currency = request.currency
        bills = request.bills
        subscriptions = request.subscriptions
        budget = request.monthly_budget

        total_bills_cost = sum(b.amount for b in bills)
        total_sub_cost = sum(s.cost for s in subscriptions if s.is_active)
        total_spend = round(total_bills_cost + total_sub_cost, 2)

        unpaid_bills = [b for b in bills if not b.is_paid]
        unpaid_amount = round(sum(b.amount for b in unpaid_bills), 2)

        # Category Breakdown
        category_totals: Dict[str, float] = {}
        for b in bills:
            category_totals[b.category] = category_totals.get(b.category, 0.0) + b.amount
        for s in subscriptions:
            if s.is_active:
                category_totals[s.category] = category_totals.get(s.category, 0.0) + s.cost

        category_breakdown = [
            CategoryBreakdown(
                category=cat,
                amount=round(amt, 2),
                percentage=round((amt / total_spend * 100), 1) if total_spend > 0 else 0.0,
            )
            for cat, amt in sorted(category_totals.items(), key=lambda item: item[1], reverse=True)
        ]

        # Budget metric
        budget_used_pct = round((total_spend / budget) * 100, 1) if budget and budget > 0 else None

        # Zombie Subscriptions
        zombie_subs = [s for s in subscriptions if s.is_active and s.last_used_days_ago and s.last_used_days_ago >= 30]

        # Synthesize via Gemini if available
        executive_summary = ""
        key_insights = []
        optimization_tips = []
        upcoming_summary = f"{len(unpaid_bills)} unpaid bill(s) totaling {currency} {unpaid_amount} due this month."

        if self._is_initialized:
            try:
                ai_digest = await self._generate_digest_with_gemini(
                    month=month,
                    currency=currency,
                    total_spend=total_spend,
                    budget=budget,
                    budget_used_pct=budget_used_pct,
                    category_breakdown=category_breakdown,
                    unpaid_amount=unpaid_amount,
                    zombie_subs=[s.service_name for s in zombie_subs],
                )
                executive_summary = ai_digest.get("executive_summary", "")
                key_insights = ai_digest.get("key_insights", [])
                optimization_tips = ai_digest.get("optimization_tips", [])
            except Exception as e:
                logger.warning("Gemini digest generation failed: %s. Using heuristic synthesizer.", e)

        # Fallback heuristic summary
        if not executive_summary:
            top_category = category_breakdown[0].category if category_breakdown else "General"
            executive_summary = (
                f"In {month}, your total scheduled and recurring commitments amount to {currency} {total_spend:,.2f} "
                f"across {len(bills)} bills and {len(subscriptions)} subscriptions. "
                f"Your largest spend category was {top_category}."
            )
            key_insights = [
                f"Active recurring subscriptions account for {currency} {total_sub_cost:,.2f} of your monthly commitments.",
                f"You currently have {len(unpaid_bills)} upcoming bills totaling {currency} {unpaid_amount:,.2f}.",
            ]
            if budget_used_pct:
                key_insights.append(f"You have committed {budget_used_pct}% of your {currency} {budget:,.2f} monthly budget.")

            optimization_tips = []
            if zombie_subs:
                z_names = ", ".join([s.service_name for s in zombie_subs])
                optimization_tips.append(
                    f"Zombie Subscription Alert: You haven't used {z_names} in over 30 days. "
                    f"Canceling could save up to {currency} {sum(s.cost for s in zombie_subs):,.2f}/month."
                )
            optimization_tips.append("Switch high-usage streaming and cloud subscriptions to annual billing to save 15-20%.")
            optimization_tips.append("Enable automated payment reminders 3 days before due dates to avoid late payment fees.")

        # Build comprehensive Markdown Report
        markdown_report = self._build_markdown_report(
            month=month,
            currency=currency,
            total_spend=total_spend,
            budget=budget,
            budget_used_pct=budget_used_pct,
            bills_count=len(bills),
            subs_count=len(subscriptions),
            unpaid_amount=unpaid_amount,
            category_breakdown=category_breakdown,
            executive_summary=executive_summary,
            key_insights=key_insights,
            optimization_tips=optimization_tips,
        )

        return MonthlyDigestResponse(
            period=month,
            total_spend=total_spend,
            total_bills_count=len(bills),
            total_subscriptions_count=len(subscriptions),
            active_subscriptions_cost=total_sub_cost,
            unpaid_bills_amount=unpaid_amount,
            category_breakdown=category_breakdown,
            budget_used_percentage=budget_used_pct,
            executive_summary=executive_summary,
            key_insights=key_insights,
            optimization_tips=optimization_tips,
            upcoming_obligations_summary=upcoming_summary,
            markdown_report=markdown_report,
            report_engine=f"gemini ({self.model_name})" if self._is_initialized else "heuristic-synthesizer",
        )

    async def _generate_digest_with_gemini(
        self,
        month: str,
        currency: str,
        total_spend: float,
        budget: Optional[float],
        budget_used_pct: Optional[float],
        category_breakdown: List[CategoryBreakdown],
        unpaid_amount: float,
        zombie_subs: List[str],
    ) -> Dict:
        """Prompts Gemini to synthesize monthly financial insights."""
        categories_str = ", ".join([f"{c.category}: {currency} {c.amount} ({c.percentage}%)" for c in category_breakdown[:5]])
        prompt = (
            f"You are an expert personal finance AI advisor. Generate a monthly financial digest for {month}.\n"
            f"- Total Committed Spend: {currency} {total_spend}\n"
            f"- Monthly Budget: {f'{currency} {budget} ({budget_used_pct}% used)' if budget else 'Not set'}\n"
            f"- Unpaid Pending Amount: {currency} {unpaid_amount}\n"
            f"- Top Expense Categories: {categories_str}\n"
            f"- Unused/Zombie Subscriptions (30+ days idle): {', '.join(zombie_subs) if zombie_subs else 'None'}\n\n"
            f"Return a strict JSON object with these keys:\n"
            f'1. "executive_summary": A professional 2-sentence overview of the user\'s monthly cash flow.\n'
            f'2. "key_insights": A list of 3 concise observations about their spending habits.\n'
            f'3. "optimization_tips": A list of 2-3 actionable tips to reduce recurring waste and save money.\n'
            f"JSON ONLY:"
        )
        response = self._model.generate_content(prompt)
        text_resp = response.text.strip()
        if text_resp.startswith("```json"):
            text_resp = text_resp[7:]
        if text_resp.startswith("```"):
            text_resp = text_resp[3:]
        if text_resp.endswith("```"):
            text_resp = text_resp[:-3]
        return json.loads(text_resp.strip())

    def _build_markdown_report(
        self,
        month: str,
        currency: str,
        total_spend: float,
        budget: Optional[float],
        budget_used_pct: Optional[float],
        bills_count: int,
        subs_count: int,
        unpaid_amount: float,
        category_breakdown: List[CategoryBreakdown],
        executive_summary: str,
        key_insights: List[str],
        optimization_tips: List[str],
    ) -> str:
        """Renders an attractive, GFM-compliant markdown report."""
        report = [
            f"# 📊 BillGuard Monthly Financial Digest — {month}",
            "",
            "> **AI Financial Intelligence Report** | Generated for smarter expense monitoring and proactive bill protection.",
            "",
            "## 📌 Executive Summary",
            f"{executive_summary}",
            "",
            "---",
            "",
            "## 💰 Financial Snapshot",
            "",
            f"- **Total Monthly Spend**: `{currency} {total_spend:,.2f}`",
            f"- **Active Subscriptions**: `{subs_count}`",
            f"- **Upcoming & Active Bills**: `{bills_count}`",
            f"- **Unpaid Obligations**: `{currency} {unpaid_amount:,.2f}`",
        ]

        if budget:
            report.append(f"- **Monthly Budget**: `{currency} {budget:,.2f}` ({budget_used_pct}% utilized)")

        report.extend([
            "",
            "### 🏷️ Spending by Category",
            "",
            "| Category | Amount | Share |",
            "| :--- | :--- | :--- |",
        ])
        for cat in category_breakdown:
            report.append(f"| **{cat.category}** | {currency} {cat.amount:,.2f} | {cat.percentage}% |")

        report.extend([
            "",
            "---",
            "",
            "## 🔍 Key Insights",
            "",
        ])
        for insight in key_insights:
            report.append(f"- {insight}")

        report.extend([
            "",
            "## 💡 Optimization & Savings Opportunities",
            "",
        ])
        for tip in optimization_tips:
            report.append(f"- 💡 {tip}")

        report.extend([
            "",
            "---",
            "*Report automatically compiled by BillGuard AI Engine.*",
        ])
        return "\n".join(report)


# Global singleton service
gemini_service = GeminiAIService()
