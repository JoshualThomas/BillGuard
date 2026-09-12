from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from app.services.token_service import ActionTokenService
from app.services.telegram_bot import TelegramBotService

router = APIRouter(prefix="/api/v1", tags=["Webhooks & Magic Actions"])


@router.get("/actions/magic-action", response_class=HTMLResponse)
async def handle_magic_action(token: str):
    """
    Handles 1-Click Magic Actions from Resend Emails (Mark as Paid, Snooze).
    No login required; validated by HMAC cryptographic signature.
    """
    payload = ActionTokenService.verify_token(token)
    if not payload:
        return HTMLResponse(
            status_code=400,
            content="""
            <!DOCTYPE html>
            <html>
            <head><title>Link Expired - BillGuard</title><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
            <body style="background:#09090b;color:#f4f4f5;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:90vh;margin:0;">
                <div style="background:#18181b;border:1px solid #27272a;padding:32px;border-radius:12px;text-align:center;max-width:400px;">
                    <h2 style="color:#ef4444;">⚠️ Link Expired or Invalid</h2>
                    <p style="color:#a1a1aa;font-size:14px;">This 1-click security token has expired or has already been used. Please log in to your BillGuard dashboard.</p>
                </div>
            </body>
            </html>
            """
        )

    action = payload.get("action")
    bill_id = payload.get("bill_id")

    if action == "mark_paid":
        heading = "✅ Bill Marked as Paid!"
        message = f"Bill #{bill_id} has been marked as paid. Your upcoming payment queue and balance have been updated."
    elif action == "snooze":
        hours = payload.get("hours", 24)
        heading = f"⏰ Reminder Snoozed for {hours} Hours"
        message = f"We have postponed alerts for Bill #{bill_id}. We'll notify you again tomorrow."
    else:
        heading = "Action Acknowledged"
        message = "Your request was processed successfully."

    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>{heading} - BillGuard</title><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body style="background:#09090b;color:#f4f4f5;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:90vh;margin:0;">
            <div style="background:#18181b;border:1px solid #27272a;padding:32px;border-radius:16px;text-align:center;max-width:420px;box-shadow:0 10px 30px rgba(0,0,0,0.5);">
                <div style="font-size:48px;margin-bottom:12px;">🛡️</div>
                <h2 style="margin:0 0 8px 0;font-size:22px;color:#ffffff;">{heading}</h2>
                <p style="color:#a1a1aa;font-size:14px;line-height:1.5;">{message}</p>
                <div style="margin-top:24px;">
                    <a href="/bills/{bill_id}" style="background:#3b82f6;color:#ffffff;text-decoration:none;padding:10px 20px;border-radius:8px;font-size:13px;font-weight:600;display:inline-block;">View in BillGuard Dashboard</a>
                </div>
            </div>
        </body>
        </html>
        """
    )


@router.post("/webhooks/telegram")
async def telegram_webhook(request: Request):
    """
    Receives incoming Telegram updates (Inline keyboard clicks, receipt uploads).
    """
    update = await request.json()
    
    # Check for callback query (inline button click)
    if "callback_query" in update:
        cq = update["callback_query"]
        cq_id = cq["id"]
        cq_data = cq.get("data", "")
        message = cq.get("message", {})
        chat_id = str(message.get("chat", {}).get("id"))
        message_id = message.get("message_id")

        result = await TelegramBotService.handle_callback_query(
            callback_query_id=cq_id,
            callback_data=cq_data,
            chat_id=chat_id,
            message_id=message_id
        )
        return JSONResponse(result)

    return JSONResponse({"status": "received"})
