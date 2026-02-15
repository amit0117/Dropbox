from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.constants.constants import MAX_FILE_SIZE_BYTES
from app.models.enums import AllowedMimeType, FileStatus


class UploadURLRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Original file name including extension.",
        examples=["report.pdf", "photo.png"]
    )
    size_bytes: int = Field(
        ...,
        gt=0,
        description="File size in bytes.",
        examples=[1048576]
    )
    mime_type: str = Field(
        ...,
        description="MIME type of the file.",
        examples=["application/pdf", "image/png"],
    )

    @field_validator("mime_type")
    @classmethod
    def validate_mime_type(cls, v: str) -> str:
        allowed_values = {member.value for member in AllowedMimeType}
        if v not in allowed_values:
            raise ValueError(f"Unsupported file type '{v}'. " f"Allowed types: {', '.join(sorted(allowed_values))}")
        return v

    @field_validator("size_bytes")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        if v > MAX_FILE_SIZE_BYTES:
            max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
            raise ValueError(f"File size ({v} bytes) exceeds the maximum allowed size of {max_mb:.0f} MB.")
        return v


class ConfirmUploadRequest(BaseModel):
    status: FileStatus = Field(..., description="New status — must be 'uploaded' or 'failed'.", examples=["uploaded", "failed"])

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: FileStatus) -> FileStatus:
        if v not in (FileStatus.UPLOADED, FileStatus.FAILED):
            raise ValueError("Status must be 'uploaded' or 'failed'.")
        return v


class UploadURLResponse(BaseModel):
    file_id: UUID
    upload_url: str
    storage_path: str


class ConfirmUploadResponse(BaseModel):
    file_id: UUID
    status: FileStatus


class FileResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    storage_path: str
    size_bytes: int
    mime_type: str
    status: FileStatus
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class FileListResponse(BaseModel):
    files: list[FileResponse]
    total: int
    skip: int
    limit: int


class DownloadURLResponse(BaseModel):
    file_id: UUID
    download_url: str
    expires_in: int = Field(
        default=3600,
        description="Seconds until the download URL expires.",
    )
