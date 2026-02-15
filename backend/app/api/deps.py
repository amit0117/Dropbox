"""
FastAPI dependency providers.

All dependencies used in route handlers are defined here so that they
can be overridden in tests via `app.dependency_overrides`.

The dependency graph:
    validate_token -> (auth — populates request.state)
    get_db_client -> DBClient singleton
    get_storage_client -> StorageClient singleton
    get_file_repository -> FileRepository(db_client)
    get_file_facade -> FileFacade(file_repository, storage_client) -> FileFacade(FileRepository(DBClient()), StorageClient())
"""

from __future__ import annotations

from fastapi import Depends

from app.core.db import DBClient
from app.core.security import validate_token  # noqa: F401 — re-exported
from app.core.storage import StorageClient
from app.facades.file_facade import FileFacade
from app.repositories.file_repository import FileRepository


def get_db_client() -> DBClient:
    return DBClient()


def get_storage_client() -> StorageClient:
    return StorageClient()


def get_file_repository(db_client: DBClient = Depends(get_db_client)) -> FileRepository:
    return FileRepository(db_client)


def get_file_facade(
    file_repository: FileRepository = Depends(get_file_repository), storage_client: StorageClient = Depends(get_storage_client)
) -> FileFacade:
    return FileFacade(file_repository, storage_client)
