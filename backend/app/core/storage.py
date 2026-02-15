from __future__ import annotations

from supabase import Client, create_client

from app.core.config import AppConfig
from app.constants.constants import PRESIGNED_URL_EXPIRY
from app.utils.logger import logger
from app.utils.singleton import SingletonMeta


class StorageClient(metaclass=SingletonMeta):

    def __init__(self) -> None:
        self._client: Client = None
        self._bucket: str = ""
        self._initialise_client()

    def _initialise_client(self) -> None:
        try:
            config = AppConfig()
            self._client = create_client(config.supabase_url, config.supabase_key)
            self._bucket = config.supabase_storage_bucket
            logger.info("Supabase Storage client initialised (bucket=%s).", self._bucket)
        except Exception as exc:
            logger.error("Failed to initialise Supabase Storage client: %s", exc)
            raise

    def create_signed_upload_url(self, path: str) -> str:
        try:
            response = self._client.storage.from_(self._bucket).create_signed_upload_url(path)
            signed_url = response.get("signed_url")
            if not signed_url:
                raise ValueError(f"Unexpected response from Storage: {response}")
            return signed_url
        except Exception as exc:
            logger.error("Failed to create signed upload URL for path=%s: %s", path, exc)
            raise

    def create_signed_download_url(
        self,
        path: str,
        expires_in: int = PRESIGNED_URL_EXPIRY,
    ) -> str:
        try:
            response = self._client.storage.from_(self._bucket).create_signed_url(path, expires_in)
            signed_url = response.get("signedURL") or response.get("signedUrl")
            if not signed_url:
                raise ValueError(f"Unexpected response from Storage: {response}")
            return signed_url
        except Exception as exc:
            logger.error("Failed to create signed download URL for path=%s: %s", path, exc)
            raise

    def delete_file(self, path: str) -> None:
        try:
            self._client.storage.from_(self._bucket).remove([path])
            logger.info("Deleted file from storage: %s", path)
        except Exception as exc:
            logger.error("Failed to delete file from storage path=%s: %s", path, exc)
            raise
