from __future__ import annotations

from datetime import datetime, timezone

from app.constants.constants import USER_FILES_TABLE
from app.core.db import DBClient
from app.models.enums import FileStatus, SupabaseOperatorType
from app.utils.logger import logger


class FileRepository:

    def __init__(self, db_client: DBClient) -> None:
        self._db = db_client

    def create(self, data: dict) -> dict:
        logger.info("Creating file record: name=%s, user_id=%s", data.get("name"), data.get("user_id"))
        return self._db.insert_row(USER_FILES_TABLE, data)

    def get_by_id(self, file_id: str, user_id: str) -> dict | None:
        return self._db.get_single_row(
            USER_FILES_TABLE,
            "*",
            where_condition_dict={"id": (SupabaseOperatorType.EQ.value, file_id), "user_id": (SupabaseOperatorType.EQ.value, user_id)},
        )

    def list_by_user(self, user_id: str, skip: int = 0, limit: int = 20) -> tuple[list[dict], int]:
        """List uploaded, non-deleted files for the user (newest first). Returns (rows, total_count)."""
        return self._db.get_rows(
            USER_FILES_TABLE,
            "*",
            where_condition_dict={
                "user_id": (SupabaseOperatorType.EQ.value, user_id),
                "status": (SupabaseOperatorType.EQ.value, FileStatus.UPLOADED.value),
                "is_deleted": (SupabaseOperatorType.EQ.value, False),
            },
            order_by_columns=[("created_at", True)],
            skip=skip,
            limit=limit
        )

    def update_status(self, file_id: str, user_id: str, status: str) -> dict | None:
        logger.info("Updating file status: file_id=%s, status=%s", file_id, status)
        return self._db.update_row(
            USER_FILES_TABLE,
            data={"status": status, "updated_at": datetime.now(timezone.utc).isoformat()},
            where_condition_dict={"id": (SupabaseOperatorType.EQ.value, file_id), "user_id": (SupabaseOperatorType.EQ.value, user_id)},
        )

    def delete(self, file_id: str, user_id: str) -> None:
        """Hard-delete the file record."""
        logger.info("Deleting file record: file_id=%s, user_id=%s", file_id, user_id)
        self._db.delete_row(
            USER_FILES_TABLE,
            where_condition_dict={"id": (SupabaseOperatorType.EQ.value, file_id), "user_id": (SupabaseOperatorType.EQ.value, user_id)},
        )
