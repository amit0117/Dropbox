"""
FastAPI application entry-point.

Creates the app instance, registers middleware (outermost → innermost),
includes route modules, and registers custom exception handlers.

Run with:
    uvicorn app.main:app --reload
or:
    python -m app.main
"""

from __future__ import annotations

import os
import uvicorn
from fastapi import FastAPI
from app.api.routes.files import router as files_router
from app.lifespan import lifespan
from app.middleware.cors_middleware import CustomCORSMiddleware
from app.utils.exceptions import register_exception_handlers
from app.utils.logger import logger

app = FastAPI(title="Dropbox API", version="1.0.0", description="Simplified Dropbox-like file storage service.", lifespan=lifespan)

# Middleware stack (order matters — outermost is added last). Execution order: CORS → Route handler
app.add_middleware(CustomCORSMiddleware)

register_exception_handlers(app)

app.include_router(files_router)
logger.info("Server initialised successfully.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    logger.info("Starting the FastAPI server at port %d", port)
    uvicorn.run(app, host="0.0.0.0", port=port)
