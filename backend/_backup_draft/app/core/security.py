"""Password hashing and JWT issuance/verification.

- Argon2id for passwords (memory-hard; resists GPU cracking).
- Short-lived access tokens, long-lived opaque-ish refresh tokens that are
  stored *hashed* server-side so they can be revoked (PRD s21
  "token expiry, least privilege").
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Literal

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from app.core.clock import utcnow
from app.core.config import get_settings
from app.core.errors import AuthenticationError

TokenType = Literal["access", "refresh"]

# OWASP-aligned Argon2id parameters; ~64 MiB, 3 passes.
_hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4, hash_len=32, salt_len=16)

MIN_PASSWORD_LENGTH = 12


@dataclass(frozen=True, slots=True)
class TokenClaims:
    subject: uuid.UUID
    roles: tuple[str, ...]
    token_type: TokenType
    jti: str
    expires_at: datetime
    node_id: str | None = None


def hash_password(password: str) -> str:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"password must be at least {MIN_PASSWORD_LENGTH} characters")
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def needs_rehash(password_hash: str) -> bool:
    try:
        return _hasher.check_needs_rehash(password_hash)
    except InvalidHashError:
        return True


def _encode(
    *,
    subject: uuid.UUID,
    roles: tuple[str, ...],
    token_type: TokenType,
    ttl_seconds: int,
    extra: dict[str, Any] | None = None,
) -> tuple[str, str, datetime]:
    settings = get_settings()
    now = utcnow()
    expires_at = now + timedelta(seconds=ttl_seconds)
    jti = uuid.uuid4().hex
    payload: dict[str, Any] = {
        "sub": str(subject),
        "roles": list(roles),
        "typ": token_type,
        "jti": jti,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }
    if extra:
        payload.update(extra)
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token, jti, expires_at


def create_access_token(
    subject: uuid.UUID, roles: tuple[str, ...], *, node_id: str | None = None
) -> tuple[str, datetime]:
    settings = get_settings()
    token, _, expires_at = _encode(
        subject=subject,
        roles=roles,
        token_type="access",  # noqa: S106 - token kind discriminator, not a secret
        ttl_seconds=settings.access_token_ttl_seconds,
        extra={"node_id": node_id} if node_id else None,
    )
    return token, expires_at


def create_refresh_token(subject: uuid.UUID, roles: tuple[str, ...]) -> tuple[str, str, datetime]:
    """Return ``(token, jti, expires_at)``. Persist only ``digest(token)``."""
    settings = get_settings()
    return _encode(
        subject=subject,
        roles=roles,
        token_type="refresh",  # noqa: S106 - token kind discriminator, not a secret
        ttl_seconds=settings.refresh_token_ttl_seconds,
    )


def decode_token(token: str, *, expect: TokenType) -> TokenClaims:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
            options={"require": ["exp", "iat", "sub", "jti", "aud", "iss"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError("token is invalid") from exc

    if payload.get("typ") != expect:
        raise AuthenticationError(f"expected a {expect} token")

    try:
        subject = uuid.UUID(str(payload["sub"]))
    except (KeyError, ValueError) as exc:
        raise AuthenticationError("token subject is malformed") from exc

    roles_claim = payload.get("roles") or []
    if not isinstance(roles_claim, list):
        raise AuthenticationError("token roles claim is malformed")

    return TokenClaims(
        subject=subject,
        roles=tuple(str(r) for r in roles_claim),
        token_type=expect,
        jti=str(payload["jti"]),
        expires_at=datetime.fromtimestamp(payload["exp"], tz=utcnow().tzinfo),
        node_id=payload.get("node_id"),
    )


def digest_token(token: str) -> str:
    """Keyed digest for refresh-token storage.

    Keyed with SECRET_KEY so a stolen database alone cannot be used to confirm
    guessed tokens offline.
    """
    settings = get_settings()
    return hmac.new(
        settings.secret_key.encode("utf-8"), token.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def generate_api_key() -> tuple[str, str]:
    """Create an edge-node API key. Returns ``(plaintext, digest)``.

    Plaintext is shown exactly once at creation time.
    """
    raw = f"ibvap_edge_{secrets.token_urlsafe(32)}"
    return raw, digest_token(raw)


def constant_time_equals(left: str, right: str) -> bool:
    return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))
