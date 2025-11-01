from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from .exceptions import AppException, DatabaseException


def error_response(status_code: int, message: str):
    return JSONResponse(
        content={"message": message, "success": False}, status_code=status_code
    )


# --- Handlers ---


async def app_exception_handler(request: Request, exe: AppException):
    return error_response(exe.status_code, exe.message)


async def database_exception_handler(request: Request, exe: DatabaseException):
    return error_response(500, exe.message)


async def generic_exception_handler(request: Request, exc: Exception):
    return error_response(500, "Internal server error. Please try again later.")


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(DatabaseException, database_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
