from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.deps import get_file_facade, validate_token
from app.constants.constants import DEFAULT_PAGE_LIMIT, DEFAULT_PAGE_SKIP, MAX_PAGE_LIMIT
from app.facades.file_facade import FileFacade
from app.models.schemas import ConfirmUploadRequest, ConfirmUploadResponse, DownloadURLResponse, FileListResponse, UploadURLRequest, UploadURLResponse

router = APIRouter(prefix="/api/v1/files", tags=["Files"], dependencies=[Depends(validate_token)])


@router.post(
    "/upload-url",
    response_model=UploadURLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a presigned upload URL",
    responses={
        400: {"description": "Invalid file type or size"},
        401: {"description": "Not authenticated"},
        502: {"description": "Storage service error"},
    },
)
def create_upload_url(body: UploadURLRequest, request: Request, facade: FileFacade = Depends(get_file_facade)) -> UploadURLResponse:
    user_id: str = request.state.user_id
    return facade.generate_upload_url(user_id, body)


@router.patch(
    "/{file_id}/confirm",
    response_model=ConfirmUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm or fail an upload",
    responses={400: {"description": "Invalid status transition"}, 401: {"description": "Not authenticated"}, 404: {"description": "File not found"}},
)
def confirm_upload(
    file_id: UUID, body: ConfirmUploadRequest, request: Request, facade: FileFacade = Depends(get_file_facade)
) -> ConfirmUploadResponse:
    """
    Transition a file from ``uploading`` to ``uploaded`` or ``failed``.

    If ``failed``, the storage object and DB record are cleaned up.
    """
    user_id: str = request.state.user_id
    return facade.confirm_upload(user_id, str(file_id), body)


@router.get(
    "",
    response_model=FileListResponse,
    status_code=status.HTTP_200_OK,
    summary="List user files (paginated)",
    responses={401: {"description": "Not authenticated"}},
)
def list_files(
    request: Request,
    skip: int = Query(default=DEFAULT_PAGE_SKIP, ge=0, description="Rows to skip"),
    limit: int = Query(default=DEFAULT_PAGE_LIMIT, ge=1, le=MAX_PAGE_LIMIT, description="Max rows to return"),
    facade: FileFacade = Depends(get_file_facade),
) -> FileListResponse:
    user_id: str = request.state.user_id
    return facade.list_files(user_id, skip=skip, limit=limit)


@router.get(
    "/{file_id}/download-url",
    response_model=DownloadURLResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a presigned download URL",
    responses={401: {"description": "Not authenticated"}, 404: {"description": "File not found"}, 502: {"description": "Storage service error"}},
)
def get_download_url(file_id: UUID, request: Request, facade: FileFacade = Depends(get_file_facade)) -> DownloadURLResponse:
    """
    Return a presigned download URL (valid for 1 hour) for the requested file.
    """
    user_id: str = request.state.user_id
    return facade.get_download_url(user_id, str(file_id))


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a file",
    responses={401: {"description": "Not authenticated"}, 404: {"description": "File not found"}},
)
def delete_file(file_id: UUID, request: Request, facade: FileFacade = Depends(get_file_facade)) -> None:
    """
    Hard-delete the file from Supabase Storage and remove the
    ``user_files`` database record.
    """
    user_id: str = request.state.user_id
    facade.delete_file(user_id, str(file_id))
