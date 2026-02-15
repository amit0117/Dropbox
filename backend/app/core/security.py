from __future__ import annotations

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.core.config import AppConfig
from app.utils.exceptions import AuthenticationError
from app.utils.logger import add_logger_metadata
from app.utils.singleton import SingletonMeta

_bearer_scheme = HTTPBearer(auto_error=False)


class SupabaseJWKSClient(metaclass=SingletonMeta):
    """Singleton JWKS client for Supabase signing keys (ES256/RS256)."""

    def __init__(self) -> None:
        config = AppConfig()
        # Supabase implements asymmetric signing using JWKS.
        jwks_url = f"{config.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
        self._client = PyJWKClient(jwks_url)

    @property
    def client(self) -> PyJWKClient:
        return self._client


def get_jwks_client() -> PyJWKClient:
    return SupabaseJWKSClient().client


def validate_token(
    request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme), jwks_client: PyJWKClient = Depends(get_jwks_client)
) -> None:
    if not credentials:
        raise AuthenticationError("Not authenticated.")
    token = credentials.credentials
    # Verify token using asymmetric signing (Supabase Signing Keys: ES256/RS256) via JWKS first.
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        decoded_token = jwt.decode(token, signing_key.key, audience="authenticated", algorithms=["ES256", "RS256"])
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError("Invalid token. Unable to decode the token.") from exc
    except Exception as exc:
        raise AuthenticationError("Not authenticated.") from exc
    request.state.user_id = decoded_token["sub"]
    request.state.user_email = decoded_token.get("email", "")
    add_logger_metadata({"user_id": request.state.user_id, "user_email": request.state.user_email})  # Add user ID and email to logger metadata
