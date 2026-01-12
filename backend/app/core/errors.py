from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


async def app_exception_handler(request: Request, exc: AppException):
    logger.error(f"AppException: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled Exception")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
