"""Consistent JSON error responses for the API."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _error_body(status_code: int, message: str, details: object | None = None) -> dict:
    body: dict = {
        "error": True,
        "status_code": status_code,
        "message": message,
    }
    if details is not None:
        body["details"] = details
    return body


async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Turn FastAPI/Starlette HTTP errors into a JSON body."""
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.status_code, str(exc.detail)),
    )


async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Invalid request data (wrong types, missing fields, etc.)."""
    return JSONResponse(
        status_code=422,
        content=_error_body(422, "Request validation failed", details=_safe_validation_errors(exc)),
    )


def _safe_validation_errors(exc: RequestValidationError) -> list[dict]:
    """Turn Pydantic errors into JSON-safe dicts (no Exception objects)."""
    safe: list[dict] = []
    for item in exc.errors():
        entry = dict(item)
        ctx = entry.get("ctx")
        if isinstance(ctx, dict):
            entry["ctx"] = {key: str(value) for key, value in ctx.items()}
        safe.append(entry)
    return safe


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch unexpected crashes so the client still gets JSON, not a stack dump."""
    from app.core.config import settings

    message = "Internal server error"
    details = None
    if settings.debug:
        details = {"type": type(exc).__name__, "detail": str(exc)}

    # Log the real error on the server so you can debug even when DEBUG=false.
    print(f"Unhandled error on {request.method} {request.url.path}: {exc!r}")

    return JSONResponse(
        status_code=500,
        content=_error_body(500, message, details=details),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all error handlers to the FastAPI app."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
