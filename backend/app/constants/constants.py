MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

USER_FILES_TABLE: str = "user_files"

PRESIGNED_URL_EXPIRY: int = 3600  # 1 hour

DEFAULT_PAGE_SKIP: int = 0
DEFAULT_PAGE_LIMIT: int = 20
MAX_PAGE_LIMIT: int = 100

ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "https://dropbox-seven-steel.vercel.app", "https://dropbox-seven-steel.vercel.app/"]
