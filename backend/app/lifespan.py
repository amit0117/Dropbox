from __future__ import annotations
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from app.core.config import AppConfig
from app.core.db import DBClient
from app.core.storage import StorageClient
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Application starting up")

    config = AppConfig()
    logger.info("Environment: %s | Port: %d | Bucket: %s", config.environment, config.port, config.supabase_storage_bucket)

    DBClient()
    StorageClient()

    logger.info("All core services initialised — ready to serve.")

    yield

    logger.info("Application shutting down…")
