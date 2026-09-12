import logging
from enum import Enum
from typing import Dict, Any, Optional, List
from app.services.email_service import EmailService
from app.services.telegram_bot import TelegramBotService

logger = logging.getLogger(__name__)


class NotificationPriority(str, Enum):
    URGENT = "urgent"    # Due in <= 1 day or severe price spike
    HIGH = "high"        # Due in <= 3 days
    NORMAL = "normal"    # Due in 7 days / weekly digest


class NotificationChannel(str, Enum):
    ALL = "all"
    EMAIL = "email"
    TELEGRAM = "telegram"


class NotificationDispatcher:
    """
    Central Asynchronous Notification Orchestrator for BillGuard.
    Handles:
    - Multi-channel delivery (Email via Resend & Mobile Push via Telegram)
    - Automatic channel fallback (if Telegram fails, fallbacks to Email)
    - Priority-aware channel escalation
    """

    @classmethod
    async def dispatch_bill_reminder(
        cls,
        user: Dict[str, Any],
        bill: Dict[str, Any],
        days_until_due: int,
        anomaly_warning: Optional[str] = None,
        preferred_channel: NotificationChannel = NotificationChannel.ALL
    ) -> Dict[str, Any]:
        """
        Dispatches a reminder across enabled channels based on user preferences and priority.
        """
        user_email = user.get("email")
        telegram_chat_id = user.get("telegram_chat_id")
        
        # Determine priority
        if days_until_due <= 1 or anomaly_warning:
            priority = NotificationPriority.URGENT
        elif days_until_due <= 3:
            priority = NotificationPriority.HIGH
        else:
            priority = NotificationPriority.NORMAL

        results: Dict[str, Any] = {
            "priority": priority.value,
            "channels_attempted": [],
            "deliveries": {},
            "errors": []
        }

        should_send_telegram = (
            telegram_chat_id and 
            preferred_channel in (NotificationChannel.ALL, NotificationChannel.TELEGRAM)
        )
        should_send_email = (
            user_email and 
            preferred_channel in (NotificationChannel.ALL, NotificationChannel.EMAIL)
        )

        # 1. Telegram Dispatch
        telegram_success = False
        if should_send_telegram:
            results["channels_attempted"].append("telegram")
            try:
                tg_res = await TelegramBotService.send_bill_alert(
                    chat_id=telegram_chat_id,
                    bill=bill,
                    days_until_due=days_until_due,
                    anomaly_warning=anomaly_warning
                )
                results["deliveries"]["telegram"] = tg_res
                if tg_res.get("status") in ("delivered", "mock_delivered"):
                    telegram_success = True
            except Exception as e:
                logger.error(f"Telegram dispatch failed: {str(e)}")
                results["errors"].append({"channel": "telegram", "error": str(e)})

        # 2. Email Dispatch (Always sent if urgent, or if user preferred email, or as fallback if telegram failed)
        if should_send_email or (not telegram_success and user_email):
            results["channels_attempted"].append("email")
            try:
                email_res = await EmailService.send_bill_reminder(
                    user_email=user_email,
                    bill=bill,
                    days_until_due=days_until_due,
                    anomaly_warning=anomaly_warning
                )
                results["deliveries"]["email"] = email_res
            except Exception as e:
                logger.error(f"Email dispatch failed: {str(e)}")
                results["errors"].append({"channel": "email", "error": str(e)})

        return results
