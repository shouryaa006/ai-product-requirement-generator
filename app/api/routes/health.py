"""Liveness check used to confirm the API is running."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return a simple OK payload. No database or AI calls."""
    return {"status": "ok"}
