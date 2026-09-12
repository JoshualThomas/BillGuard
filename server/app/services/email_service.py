import os
import base64
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import httpx
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.services.token_service import ActionTokenService

logger = logging.getLogger(__name__)

# Configure Jinja2 template loader
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)


class EmailService:
    """
    Production-ready Resend Email Service for BillGuard.
    Includes:
    - 1-Click Signed Magic Actions (Mark as Paid, Snooze)
    - Dynamic RFC 5545 .ics Calendar Attachments
    - Resend API Dispatcher with Mock Fallback for local tests
    """

    @staticmethod
    def generate_ics_calendar_invite(
        vendor: str,
        due_date: datetime,
        amount: float,
        currency_symbol: str = "₹",
        bill_id: str = "1"
    ) -> str:
        """
        Generates standard RFC 5545 iCalendar content with alarms.
        Compatible with Google Calendar, Apple Calendar, and Outlook.
        """
        dt_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        dt_start = due_date.strftime("%Y%m%d")
        dt_end = (due_date + timedelta(days=1)).strftime("%Y%m%d")
        uid = f"billguard-{bill_id}-{int(due_date.timestamp())}@billguard.app"

        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//BillGuard//Financial Assistant//EN
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dt_stamp}
DTSTART;VALUE=DATE:{dt_start}
DTEND;VALUE=DATE:{dt_end}
SUMMARY:💸 Pay Bill: {vendor} ({currency_symbol}{amount:,.2f})
DESCRIPTION:BillGuard reminder to pay {vendor}. Total amount due: {currency_symbol}{amount:,.2f}.
STATUS:CONFIRMED
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:BillGuard Alert: {vendor} is due tomorrow!
END:VALARM
BEGIN:VALARM
TRIGGER:-PT2H
ACTION:DISPLAY
DESCRIPTION:BillGuard Final Notice: {vendor} due in 2 hours!
END:VALARM
END:VEVENT
END:VCALENDAR
"""
        return ics_content

    @classmethod
    async def send_bill_reminder(
        cls,
        user_email: str,
        bill: Dict[str, Any],
        days_until_due: int,
        anomaly_warning: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dispatches a rich bill reminder email with 1-click magic actions and .ics attachment.
        """
        # Determine urgency and badges
        if days_until_due <= 1:
            alert_tier = "URGENT • DUE IN 24H"
            badge_class = "badge-urgent"
            message_lead = f"Immediate action needed: your payment for {bill.get('vendor')} is due in 24 hours."
        elif days_until_due <= 3:
            alert_tier = "PRIORITY • DUE IN 3 DAYS"
            badge_class = "badge-warning"
            message_lead = f"Heads up: your {bill.get('vendor')} bill is due in 3 days."
        else:
            alert_tier = "UPCOMING • DUE IN 7 DAYS"
            badge_class = "badge-info"
            message_lead = f"Advance reminder: your scheduled payment for {bill.get('vendor')} is approaching."

        bill_id = str(bill.get("id", "test-bill-1"))
        user_id = str(bill.get("user_id", "test-user-1"))

        # Generate HMAC 1-Click Magic Tokens
        paid_token = ActionTokenService.generate_token({
            "action": "mark_paid",
            "bill_id": bill_id,
            "user_id": user_id
        })
        snooze_token = ActionTokenService.generate_token({
            "action": "snooze",
            "bill_id": bill_id,
            "user_id": user_id,
            "hours": 24
        })

        magic_mark_paid_url = f"{settings.BACKEND_URL}/api/v1/actions/magic-action?token={paid_token}"
        magic_snooze_url = f"{settings.BACKEND_URL}/api/v1/actions/magic-action?token={snooze_token}"
        dashboard_bill_url = f"{settings.FRONTEND_URL}/bills/{bill_id}"

        # Parse due date
        raw_due_date = bill.get("due_date")
        if isinstance(raw_due_date, str):
            try:
                due_date_obj = datetime.fromisoformat(raw_due_date)
            except ValueError:
                due_date_obj = datetime.now(timezone.utc) + timedelta(days=days_until_due)
        elif isinstance(raw_due_date, datetime):
            due_date_obj = raw_due_date
        else:
            due_date_obj = datetime.now(timezone.utc) + timedelta(days=days_until_due)

        due_date_formatted = due_date_obj.strftime("%B %d, %Y")

        # Render HTML template
        template = jinja_env.get_template("bill_alert.html")
        html_content = template.render(
            bill=bill,
            user_email=user_email,
            alert_tier=alert_tier,
            badge_class=badge_class,
            message_lead=message_lead,
            due_date_formatted=due_date_formatted,
            anomaly_warning=anomaly_warning,
            magic_mark_paid_url=magic_mark_paid_url,
            magic_snooze_url=magic_snooze_url,
            dashboard_bill_url=dashboard_bill_url
        )

        # Generate iCal attachment
        ics_text = cls.generate_ics_calendar_invite(
            vendor=bill.get("vendor", "Utility"),
            due_date=due_date_obj,
            amount=float(bill.get("amount", 0.0)),
            currency_symbol=bill.get("currency_symbol", "₹"),
            bill_id=bill_id
        )
        ics_base64 = base64.b64encode(ics_text.encode("utf-8")).decode("utf-8")

        subject = f"[{alert_tier.split('•')[0].strip()}] Pay {bill.get('vendor')} ({bill.get('currency_symbol', '₹')}{bill.get('amount', 0):,.2f}) due {due_date_formatted}"

        # Check for Resend API Key
        if not settings.RESEND_API_KEY or settings.RESEND_API_KEY.startswith("re_placeholder"):
            logger.warning("No valid RESEND_API_KEY provided. Operating in Mock Mode.")
            return {
                "status": "mock_delivered",
                "to": user_email,
                "subject": subject,
                "provider": "resend (mock)",
                "magic_mark_paid_url": magic_mark_paid_url
            }

        # Dispatch via Resend API
        payload = {
            "from": settings.EMAIL_FROM,
            "to": [user_email],
            "subject": subject,
            "html": html_content,
            "attachments": [
                {
                    "filename": f"bill-{bill.get('vendor', 'reminder').lower().replace(' ', '-')}.ics",
                    "content": ics_base64
                }
            ]
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=payload
            )

            if response.status_code in (200, 201):
                data = response.json()
                logger.info(f"Email delivered via Resend. ID: {data.get('id')}")
                return {"status": "delivered", "id": data.get("id"), "to": user_email}
            else:
                logger.error(f"Resend API error: {response.status_code} - {response.text}")
                return {"status": "error", "error": response.text, "code": response.status_code}
