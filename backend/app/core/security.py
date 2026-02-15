from __future__ import annotations  # used for type hints
import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.constants.constants import SYSTEM_USER_ID, SYSTEM_USER_EMAIL
from app.core.config import AppConfig
from app.utils.exceptions import AuthenticationError
from app.utils.logger import add_logger_metadata

_bearer_scheme = HTTPBearer(auto_error=False)


def validate_token(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme)) -> None:
    if not credentials:
        raise AuthenticationError("Not authenticated.")
    token = credentials.credentials
    config = AppConfig()
    try:
        if config.is_development:
            # In development mode bypass real JWT verification
            decoded_token: dict = {"sub": SYSTEM_USER_ID, "email": SYSTEM_USER_EMAIL}
        else:
            decoded_token = jwt.decode(token, config.supabase_jwt_secret, audience="authenticated", algorithms=["HS256"])

        request.state.user_id = decoded_token["sub"]
        request.state.user_email = decoded_token.get("email", "")
        # Add user ID and email to logger metadata
        add_logger_metadata({"user_id": request.state.user_id, "user_email": request.state.user_email})
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError("Invalid token. Unable to decode the token.") from exc
    except Exception as exc:
        raise AuthenticationError("Not authenticated.") from exc
