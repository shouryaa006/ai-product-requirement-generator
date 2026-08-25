"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.prd import router as prd_router
from app.core.config import settings
from app.core.errors import register_exception_handlers

app = FastAPI(
    title=settings.app_name,
    description="Backend API for generating structured product requirements from natural language.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

register_exception_handlers(app)
app.include_router(health_router)
app.include_router(prd_router)
