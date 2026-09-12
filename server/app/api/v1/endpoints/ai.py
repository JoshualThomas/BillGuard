"""
FastAPI Endpoints for AI & Intelligence Services.
Deliverables for Joshual Thomas (AI & Intelligence Engineer):
1. Multimodal receipt/invoice parser endpoint
2. Anomaly & price-hike detection endpoint
3. AI monthly financial digest generator endpoint
"""
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from typing import Optional

from app.schemas.ai import (
    AIStatusResponse,
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    MonthlyDigestRequest,
    MonthlyDigestResponse,
    ReceiptParseResponse,
)
from app.services.gemini_service import gemini_service

router = APIRouter()

SUPPORTED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "application/pdf",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ---------------------------------------------------------------------------
# 1. Multimodal Bill & Receipt Ingestion Endpoint
# ---------------------------------------------------------------------------
@router.post(
    "/parse-receipt",
    response_model=ReceiptParseResponse,
    status_code=status.HTTP_200_OK,
    summary="Parse receipt or invoice document (Multimodal OCR)",
    description="Uploads a receipt image (JPEG, PNG, WEBP) or PDF invoice and uses Google Gemini Flash "
                "to extract vendor, dates, categories, totals, line items, and recurrence frequency.",
)
async def parse_receipt(
    file: UploadFile = File(..., description="Invoice or receipt image/PDF file"),
    currency_hint: Optional[str] = Form(default="USD", description="Default currency hint (e.g., USD, INR, EUR)"),
) -> ReceiptParseResponse:
    """Multimodal document parsing endpoint powered by Google Gemini."""
    content_type = file.content_type or ""
    filename = file.filename or "receipt"

    # Validate file format
    is_valid_mime = content_type.lower() in SUPPORTED_MIME_TYPES
    is_valid_ext = any(filename.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".pdf"])

    if not is_valid_mime and not is_valid_ext:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{content_type}'. Supported formats: PDF, JPEG, PNG, WEBP.",
        )

    # Read binary payload
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE // (1024 * 1024)}MB.",
        )

    try:
        result = await gemini_service.parse_receipt_multimodal(
            file_bytes=file_bytes,
            filename=filename,
            content_type=content_type or "application/octet-stream",
            currency_hint=currency_hint or "USD",
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process receipt: {str(e)}",
        )


# ---------------------------------------------------------------------------
# 2. Smart Anomaly & Price-Hike Detection Endpoint
# ---------------------------------------------------------------------------
@router.post(
    "/detect-anomalies",
    response_model=AnomalyDetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect price spikes, subscription hikes, and billing anomalies",
    description="Compares a current bill against trailing historical records to identify abnormal surges, "
                "silent subscription fee increases, or duplicate billings, returning actionable AI reasoning.",
)
async def detect_anomalies(request: AnomalyDetectionRequest) -> AnomalyDetectionResponse:
    """Anomaly and price-hike detection endpoint using statistical analysis and Gemini AI."""
    try:
        return await gemini_service.detect_anomalies(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating bill anomalies: {str(e)}",
        )


# ---------------------------------------------------------------------------
# 3. AI Monthly Financial Digest Generator Endpoint
# ---------------------------------------------------------------------------
@router.post(
    "/monthly-digest",
    response_model=MonthlyDigestResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate comprehensive AI monthly financial digest",
    description="Aggregates monthly bills, active subscriptions, and spending patterns into a personalized "
                "financial executive summary with category breakdowns, zombie subscription alerts, and optimization tips.",
)
async def generate_monthly_digest(request: MonthlyDigestRequest) -> MonthlyDigestResponse:
    """Monthly financial intelligence report and digest generator."""
    try:
        return await gemini_service.generate_monthly_digest(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating monthly digest: {str(e)}",
        )


# ---------------------------------------------------------------------------
# 4. Service Status & Health
# ---------------------------------------------------------------------------
@router.get(
    "/status",
    response_model=AIStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get AI intelligence service status",
)
async def get_ai_status() -> AIStatusResponse:
    """Returns runtime status and readiness of the Gemini AI intelligence engine."""
    is_live = gemini_service.is_configured
    return AIStatusResponse(
        service="BillGuard AI Engine",
        gemini_configured=is_live,
        gemini_model=gemini_service.model_name,
        supported_file_types=list(SUPPORTED_MIME_TYPES),
        status="ready" if is_live else "ready_fallback_mode",
    )
