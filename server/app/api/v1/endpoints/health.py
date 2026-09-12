"""
Health check endpoints for BillGuard API.
"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "BillGuard API"
    version: str = "0.1.0"


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint to verify backend service availability."""
    return HealthResponse(status="ok", service="BillGuard API", version="0.1.0")
