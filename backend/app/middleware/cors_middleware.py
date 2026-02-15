from __future__ import annotations
import os
from starlette.middleware.cors import CORSMiddleware
from app.constants.constants import ALLOWED_ORIGINS


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
