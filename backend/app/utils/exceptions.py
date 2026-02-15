from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.utils.logger import logger


class DropboxAppException(Exception):

    def __init__(self, message: str = "An unexpected error occurred."):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(DropboxAppException):

    def __init__(self, message: str = "Not authenticated."):
        super().__init__(message)


class AuthorizationError(DropboxAppException):

    def __init__(self, message: str = "Access denied."):
        super().__init__(message)


class FileNotFoundError(DropboxAppException):

    def __init__(self, message: str = "File not found."):
        super().__init__(message)


class FileAlreadyExistsError(DropboxAppException):

    def __init__(self, message: str = "File already exists."):
        super().__init__(message)


class FileValidationError(DropboxAppException):

    def __init__(self, message: str = "File validation failed."):
        super().__init__(message)


class StorageError(DropboxAppException):

    def __init__(self, message: str = "Storage operation failed."):
        super().__init__(message)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AuthenticationError)
    async def _handle_authentication_error(request: Request, exc: AuthenticationError) -> JSONResponse:
        logger.warning("AuthenticationError: %s", exc.message)
        return JSONResponse(status_code=401, content={"detail": exc.message})

    @app.exception_handler(AuthorizationError)
    async def _handle_authorization_error(request: Request, exc: AuthorizationError) -> JSONResponse:
        logger.warning("AuthorizationError: %s", exc.message)
        return JSONResponse(status_code=403, content={"detail": exc.message})

    @app.exception_handler(FileNotFoundError)
    async def _handle_file_not_found(request: Request, exc: FileNotFoundError) -> JSONResponse:
        logger.info("FileNotFoundError: %s", exc.message)
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(FileAlreadyExistsError)
    async def _handle_file_already_exists(request: Request, exc: FileAlreadyExistsError) -> JSONResponse:
        logger.info("FileAlreadyExistsError: %s", exc.message)
        return JSONResponse(status_code=409, content={"detail": exc.message})

    @app.exception_handler(FileValidationError)
    async def _handle_file_validation_error(request: Request, exc: FileValidationError) -> JSONResponse:
        logger.info("FileValidationError: %s", exc.message)
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(StorageError)
    async def _handle_storage_error(request: Request, exc: StorageError) -> JSONResponse:
        logger.error("StorageError: %s", exc.message)
        return JSONResponse(status_code=502, content={"detail": exc.message})

    @app.exception_handler(Exception)
    async def _handle_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", str(exc))
        return JSONResponse(status_code=500, content={"detail": "Internal server error."})
