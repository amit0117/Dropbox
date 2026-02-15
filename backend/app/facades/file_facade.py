from __future__ import annotations
import uuid
from datetime import datetime, timezone
from app.constants.constants import PRESIGNED_URL_EXPIRY
from app.core.storage import StorageClient
from app.models.enums import FileStatus
from app.models.schemas import (
    ConfirmUploadRequest,
    ConfirmUploadResponse,
    DownloadURLResponse,
    FileListResponse,
    FileResponse,
    UploadURLRequest,
    UploadURLResponse,
)
from app.repositories.file_repository import FileRepository
from app.utils.exceptions import FileNotFoundError, FileValidationError, StorageError
from app.utils.logger import logger


class FileFacade:

    def __init__(self, file_repository: FileRepository, storage_client: StorageClient) -> None:
        self._file_repo = file_repository
        self._storage_client = storage_client

    def generate_upload_url(self, user_id: str, request: UploadURLRequest) -> UploadURLResponse:
        """
        Create a DB record (status=uploading) and return a presigned
        upload URL so the client can push the file directly to storage.
        """
        file_id = str(uuid.uuid4())
        storage_path = self._build_storage_path(user_id, file_id, request.name)

        # 1. Generate presigned upload URL from Supabase Storage
        try:
            upload_url = self._storage_client.create_signed_upload_url(storage_path)
        except Exception as exc:
            logger.error("Storage upload URL generation failed: %s", exc)
            raise StorageError("Unable to generate upload URL. Please try again.") from exc

        # 2. Persist file metadata with status='uploading'
        now = datetime.now(timezone.utc).isoformat()
        record = self._file_repo.create(
            {
                "id": file_id,
                "user_id": user_id,
                "name": request.name,
                "storage_path": storage_path,
                "size_bytes": request.size_bytes,
                "mime_type": request.mime_type,
                "status": FileStatus.UPLOADING.value,
                "is_deleted": False,
                "created_at": now,
                "updated_at": now,
            }
        )

        logger.info("Upload URL generated: file_id=%s, user_id=%s", file_id, user_id)

        return UploadURLResponse(file_id=record["id"], upload_url=upload_url, storage_path=storage_path)

    def confirm_upload(self, user_id: str, file_id: str, request: ConfirmUploadRequest) -> ConfirmUploadResponse:
        existing = self._file_repo.get_by_id(file_id, user_id)
        if not existing:
            raise FileNotFoundError("File not found or access denied.")

        if existing["status"] != FileStatus.UPLOADING.value:
            raise FileValidationError(f"File status is '{existing['status']}'; only 'uploading' " f"files can be confirmed.")

        new_status = request.status.value

        if new_status == FileStatus.FAILED.value:
            self._safe_delete_storage(existing["storage_path"])
            self._file_repo.delete(file_id, user_id)
            logger.info("Upload marked as failed — cleaned up file_id=%s", file_id)
        else:
            self._file_repo.update_status(file_id, user_id, new_status)
            logger.info("Upload confirmed: file_id=%s", file_id)

        return ConfirmUploadResponse(file_id=uuid.UUID(file_id), status=request.status)

    def list_files(self, user_id: str, skip: int = 0, limit: int = 20) -> FileListResponse:
        rows, total = self._file_repo.list_by_user(user_id, skip=skip, limit=limit)

        files = [FileResponse(**row) for row in rows]
        return FileListResponse(files=files, total=total, skip=skip, limit=limit)

    def get_download_url(self, user_id: str, file_id: str) -> DownloadURLResponse:
        """Generate a presigned download URL for an uploaded file."""
        existing = self._file_repo.get_by_id(file_id, user_id)
        if not existing:
            raise FileNotFoundError("File not found or access denied.")

        if existing["status"] != FileStatus.UPLOADED.value:
            raise FileValidationError("File is not in 'uploaded' state.")

        if existing.get("is_deleted"):
            raise FileNotFoundError("File has been deleted.")

        try:
            download_url = self._storage_client.create_signed_download_url(existing["storage_path"], expires_in=PRESIGNED_URL_EXPIRY)
        except Exception as exc:
            logger.error("Storage download URL generation failed: %s", exc)
            raise StorageError("Unable to generate download URL. Please try again.") from exc

        return DownloadURLResponse(file_id=uuid.UUID(file_id), download_url=download_url, expires_in=PRESIGNED_URL_EXPIRY)

    def delete_file(self, user_id: str, file_id: str) -> None:
        existing = self._file_repo.get_by_id(file_id, user_id)
        if not existing:
            raise FileNotFoundError("File not found or access denied.")

        self._safe_delete_storage(existing["storage_path"])
        self._file_repo.delete(file_id, user_id)
        logger.info("File deleted: file_id=%s, user_id=%s", file_id, user_id)

    @staticmethod
    def _build_storage_path(user_id: str, file_id: str, filename: str) -> str:
        return f"{user_id}/{file_id}/{filename}"

    def _safe_delete_storage(self, storage_path: str) -> None:
        try:
            self._storage_client.delete_file(storage_path)
        except Exception as exc:
            logger.warning("Failed to delete storage object at '%s': %s", storage_path, exc)
