import logging
import time

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)

# Fixed dev user ID used when APP_ENV=development and NO token is provided
_DEV_USER_ID = "00000000-0000-0000-0000-000000000001"

# In-memory JWKS cache
_jwks_cache: dict | None = None
_jwks_cache_time: float = 0.0
_JWKS_CACHE_TTL = 3600  # 1 hour


async def _fetch_jwks() -> dict:
    """Fetch JWKS from Supabase, with a 1-hour in-memory cache."""
    global _jwks_cache, _jwks_cache_time

    now = time.monotonic()
    if _jwks_cache is not None and (now - _jwks_cache_time) < _JWKS_CACHE_TTL:
        return _jwks_cache

    jwks_url = settings.supabase_jwks_url
    if not jwks_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "JWKS_NOT_CONFIGURED",
                    "message": "JWKS URL is not configured.",
                }
            },
        )

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(jwks_url)
        resp.raise_for_status()
        _jwks_cache = resp.json()
        _jwks_cache_time = time.monotonic()
        return _jwks_cache


def _find_signing_key(jwks: dict, token: str) -> dict:
    """Match the JWT kid header to a key in the JWKS keyset."""
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": {
                "code": "INVALID_TOKEN",
                "message": "Unable to find matching signing key.",
            }
        },
    )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    """Verify Supabase JWT via JWKS and extract user id.

    In development mode, returns a fixed dev user ID only when no token
    is provided at all.  When a token IS provided, always extract the
    real ``sub`` claim so the user identity stays consistent.
    """
    if credentials is None or not credentials.credentials:
        if settings.app_env == "development":
            logger.debug("No token provided — using dev user ID")
            return _DEV_USER_ID
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "MISSING_TOKEN",
                    "message": "Authorization token is required.",
                }
            },
        )

    token = credentials.credentials

    # If JWKS URL is not set, fall back depending on environment
    if not settings.supabase_jwks_url:
        if settings.app_env == "development":
            logger.debug("JWKS URL not configured — decoding token without verification")
            return _decode_unverified(token)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "JWKS_NOT_CONFIGURED",
                    "message": "JWKS URL is not configured.",
                }
            },
        )

    try:
        jwks = await _fetch_jwks()
        signing_key = _find_signing_key(jwks, token)

        # Supabase JWT signing keys may be RSA (RS256) or ECC (ES256). The kid
        # match + JWKS signature verification already pin the exact key; accept
        # both algorithms so ES256-signed tokens are not rejected.
        payload = jwt.decode(
            token,
            key=signing_key,
            algorithms=["RS256", "ES256"],
            audience=settings.supabase_jwt_audience,
            issuer=settings.supabase_jwt_issuer or None,
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {"code": "INVALID_TOKEN", "message": "Invalid token."}
                },
            )
        return user_id
    except HTTPException:
        raise
    except (JWTError, httpx.HTTPError, KeyError, ValueError) as exc:
        if settings.app_env == "development":
            logger.warning(
                "JWKS verification failed (%s: %s) — falling back to unverified decode",
                type(exc).__name__,
                exc,
            )
            return _decode_unverified(token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "Invalid or expired token.",
                }
            },
        )


def _decode_unverified(token: str) -> str:
    """Decode a JWT without signature verification (dev-only fallback).

    Skips signature, audience, and expiration checks so the real ``sub``
    claim is always extracted regardless of token age or signing key.
    """
    try:
        payload = jwt.decode(
            token,
            key="",
            algorithms=["RS256", "HS256"],
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_exp": False,
            },
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            logger.warning("Token has no 'sub' claim — using dev user ID")
            return _DEV_USER_ID
        return user_id
    except JWTError as exc:
        logger.warning("Unverified decode failed (%s) — using dev user ID", exc)
        return _DEV_USER_ID
