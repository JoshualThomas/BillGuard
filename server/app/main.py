from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.webhooks import router as webhooks_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent financial assistant for bill tracking, anomaly detection, and automated notifications.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(webhooks_router)


@app.get("/health", tags=["Health & DevOps"])
async def health_check():
    """
    Health check endpoint for Render/Railway/Docker deployment monitoring.
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "service": settings.PROJECT_NAME,
        "version": "1.0.0"
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to BillGuard API",
        "docs": "/docs",
        "health": "/health"
    }
