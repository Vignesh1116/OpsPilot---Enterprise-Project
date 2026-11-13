import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base class for domain and application level exceptions."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_SERVER_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details={"resource": resource, "identifier": str(identifier)},
        )


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Invalid or expired authentication credentials."):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
        )


class ForbiddenError(AppException):
    def __init__(self, message: str = "You do not possess permission to perform this action."):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
        )


class ConflictError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="RESOURCE_CONFLICT",
            details=details,
        )


class ValidationError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Registers RFC 7807 problem details exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning(
            "Application exception: %s | path=%s error_code=%s",
            exc.message,
            request.url.path,
            exc.error_code,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": f"https://opspilot.internal/errors/{exc.error_code.lower()}",
                "title": exc.error_code,
                "status": exc.status_code,
                "detail": exc.message,
                "instance": request.url.path,
                "details": exc.details,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.info("Request validation failed on %s: %s", request.url.path, exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "type": "https://opspilot.internal/errors/validation-error",
                "title": "VALIDATION_ERROR",
                "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "detail": "The request payload failed schema validation.",
                "instance": request.url.path,
                "details": {"validation_errors": exc.errors()},
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": "https://opspilot.internal/errors/http-error",
                "title": "HTTP_ERROR",
                "status": exc.status_code,
                "detail": exc.detail,
                "instance": request.url.path,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled server exception on %s: %s", request.url.path, str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "type": "https://opspilot.internal/errors/internal-server-error",
                "title": "INTERNAL_SERVER_ERROR",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "detail": "An unexpected error occurred while processing the request.",
                "instance": request.url.path,
            },
        )
