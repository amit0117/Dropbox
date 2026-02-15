
import os
from dotenv import load_dotenv

from app.utils.singleton import SingletonMeta

load_dotenv()


class AppConfig(metaclass=SingletonMeta):
    """
    Centralised, read-only application configuration.

    All values are read once during __init__ and cached for the lifetime
    of the process.
    """

    def __init__(self) -> None:
        self.supabase_url: str = self._require("SUPABASE_URL")
        self.supabase_key: str = self._require("SUPABASE_KEY")
        self.supabase_jwt_secret: str = self._require("SUPABASE_JWT_SECRET")
        self.supabase_storage_bucket: str = self._require("SUPABASE_STORAGE_BUCKET")
        self.environment: str = os.environ.get("ENVIRONMENT", "development")
        self.port: int = int(os.environ.get("PORT", "8080"))
        self.allowed_origins: list[str] = self._parse_list(os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000"))

    @staticmethod
    def _require(key: str) -> str:
        value = os.environ.get(key)
        if not value:
            raise EnvironmentError(f"Required environment variable '{key}' is not set.")
        return value

    @staticmethod
    def _parse_list(raw: str, sep: str = ",") -> list[str]:
        return [item.strip() for item in raw.split(sep) if item.strip()]

    @property
    def is_development(self) -> bool:
        return self.environment in ("development", "dev")
