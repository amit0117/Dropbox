from __future__ import annotations
import os
from starlette.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "https://dropbox-seven-steel.vercel.app"]


class CustomCORSMiddleware(CORSMiddleware):
    def __init__(self, app):
        allowed_origins = ["*"] if os.environ.get("ENVIRONMENT") in ("development", "dev") else ALLOWED_ORIGINS
        super().__init__(
            app,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
        )
