"""Load settings from environment variables (.env is optional)."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field


# Project root: .../ai-product-requirement-generator
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


class Settings(BaseModel):
    """App settings. Values come from environment variables when present."""

    app_name: str = Field(default="AI Product Requirement Generator")
    debug: bool = Field(default=False)
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-2.5-flash")

    model_config = {"extra": "ignore"}


def get_settings() -> Settings:
    """Build settings from environment variables with safe defaults."""
    debug_raw = os.getenv("DEBUG", "false").strip().lower()
    port_raw = os.getenv("PORT", "8000").strip()

    return Settings(
        app_name=os.getenv("APP_NAME", "AI Product Requirement Generator"),
        debug=debug_raw in {"1", "true", "yes", "on"},
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(port_raw) if port_raw.isdigit() else 8000,
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash",
    )


settings = get_settings()
