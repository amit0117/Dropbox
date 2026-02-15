"""
Vercel entrypoint: re-export the FastAPI app so Vercel finds it at app/index.py.
"""
from app.main import app

__all__ = ["app"]
