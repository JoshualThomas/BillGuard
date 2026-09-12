"""
API v1 Router registry uniting all modular endpoint routers.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import ai, health

api_router = APIRouter()

# Register modular routes
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI & Intelligence"])
