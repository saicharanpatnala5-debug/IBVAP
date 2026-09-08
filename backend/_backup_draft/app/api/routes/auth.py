"""Authentication routes: login, refresh, logout, edge-node token exchange."""

from __future__ import annotations

from datetime import timedelta
from functools import lru_cache

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentPrincipal, DbSession, client_ip, require
from app.core.clock import utcnow
from app.core.config import get_settings
from app.core.errors import AuthenticationError, ConflictError, NotFoundError
from app.core.rbac import Permission, Role
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    digest_token,
    generate_api_key,
    hash_password,
    needs_rehash,
    verify_password,
)
from app.db.enums import AuditResult
from app.db.models.user import EdgeNode, RefreshToken, User
from app.schemas.auth import (
    CurrentUser,
    EdgeNodeCreate,
    EdgeNodeCreated,
    EdgeTokenRequest,
    LoginRequest,
    PasswordChange,
    RefreshRequest,
    TokenPair,
    UserCreate,
    UserRead,
    UserUpdate,
)
from app.services import audit

router = APIRouter(prefix="/auth", tags=["auth"])

#: Failed-login threshold before a temporary lockout. Slows credential stuffing
#: without giving an attacker a trivial way to lock out a real operator forever.
_MAX_FAILED_LOGINS = 5
_LOCKOUT_MINUTES = 15


@router.post("/login", response_model=TokenPair)
async def login(
    payload: LoginRequest,
    request: Request,
    session: DbSession,
) -> TokenPair:
    settings = get_settings()
    now = utcnow()
    email = payload.email.lower().strip()

    user = (
        await session.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()

    async def _fail(reason: str) -> None:
        await audit.record(
            session,
            action=audit.ACTION_LOGIN_FAILED,
            actor_label=email,
            actor_id=user.id if user else None,
            object_type="user",
            object_id=user.id if user else None,
            result=AuditResult.FAILURE,
            source_ip=client_ip(request),
            user_agent=request.headers.get("user-agent"),
            context={"reason": reason},
        )
        await session.commit()

    if user is None:
        # Still run a hash comparison so a missing account and a wrong password
        # take comparable time; otherwise the endpoint enumerates valid emails.
        verify_password(payload.password, _dummy_hash())
        await _fail("unknown_email")
        raise AuthenticationError("invalid credentials")

    if user.locked_until and user.locked_until > now:
        await _fail("account_locked")
        raise AuthenticationError("account is temporarily locked; try again later")

    if not user.is_active:
        await _fail("account_disabled")
        raise AuthenticationError("invalid credentials")

    if not verify_password(payload.password, user.password_hash):
        user.failed_login_count += 1
        if user.failed_login_count >= _MAX_FAILED_LOGINS:
            user.locked_until = now + timedelta(minutes=_LOCKOUT_MINUTES)
            user.failed_login_count = 0
        await _fail("bad_password")
        raise AuthenticationError("invalid credentials")

    # Upgrade the stored hash if Argon2 parameters have since been raised.
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(payload.password)

    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = now

    roles = tuple(str(r) for r in (user.roles or ()))
    access_token, expires_at = create_access_token(user.id, roles)
    refresh_token, jti, refresh_expires = create_refresh_token(user.id, roles)

    session.add(
        RefreshToken(
            user_id=user.id,
            jti=jti,
            token_digest=digest_token(refresh_token),
            issued_at=now,
            expires_at=refresh_expires,
            user_agent=(request.headers.get("user-agent") or "")[:255] or None,
            source_ip=client_ip(request),
        )
    )

    await audit.record(
        session,
        action=audit.ACTION_LOGIN,
        actor_label=user.email,
        actor_id=user.id,
        actor_roles=list(roles),
        object_type="user",
        object_id=user.id,
        source_ip=client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    await session.commit()

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
        expires_in=settings.access_token_ttl_seconds,
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    payload: RefreshRequest,
    request: Request,
    session: DbSession,
) -> TokenPair:
    """Rotate a refresh token.

    Rotation is single-use. Presenting a token that was already rotated means
    either a replay or a stolen token, so the entire family is revoked and the
    event is audited.
    """
    settings = get_settings()
    claims = decode_token(payload.refresh_token, expect="refresh")
    digest = digest_token(payload.refresh_token)

    record = (
        await session.execute(
            select(RefreshToken).where(RefreshToken.token_digest == digest)
        )
    ).scalar_one_or_none()

    if record is None:
        raise AuthenticationError("refresh token is not recognised")

    now = utcnow()
    if record.revoked_at is not None or record.replaced_by_id is not None:
        await _revoke_family(session, record.user_id)
        await audit.record(
            session,
            action=audit.ACTION_TOKEN_REUSE,
            actor_label=str(record.user_id),
            actor_id=record.user_id,
            object_type="refresh_token",
            object_id=record.id,
            result=AuditResult.FAILURE,
            source_ip=client_ip(request),
            context={"detail": "rotated token presented again; all sessions revoked"},
        )
        await session.commit()
        raise AuthenticationError("refresh token has already been used")

    if record.expires_at <= now:
        raise AuthenticationError("refresh token has expired")

    user = (
        await session.execute(select(User).where(User.id == claims.subject))
    ).scalar_one_or_none()
    if user is None or not user.is_active:
        raise AuthenticationError("user is unknown or deactivated")

    roles = tuple(str(r) for r in (user.roles or ()))
    access_token, expires_at = create_access_token(user.id, roles)
    new_refresh, jti, refresh_expires = create_refresh_token(user.id, roles)

    replacement = RefreshToken(
        user_id=user.id,
        jti=jti,
        token_digest=digest_token(new_refresh),
        issued_at=now,
        expires_at=refresh_expires,
        user_agent=(request.headers.get("user-agent") or "")[:255] or None,
        source_ip=client_ip(request),
    )
    session.add(replacement)
    await session.flush()

    record.revoked_at = now
    record.replaced_by_id = replacement.id

    await audit.record(
        session,
        action=audit.ACTION_TOKEN_REFRESH,
        actor_label=user.email,
        actor_id=user.id,
        object_type="refresh_token",
        object_id=replacement.id,
        source_ip=client_ip(request),
    )
    await session.commit()

    return TokenPair(
        access_token=access_token,
        refresh_token=new_refresh,
        expires_at=expires_at,
        expires_in=settings.access_token_ttl_seconds,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: RefreshRequest,
    request: Request,
    principal: CurrentPrincipal,
    session: DbSession,
) -> None:
    digest = digest_token(payload.refresh_token)
    record = (
        await session.execute(
            select(RefreshToken).where(
                RefreshToken.token_digest == digest,
                RefreshToken.user_id == principal.id,
            )
        )
    ).scalar_one_or_none()
    if record is not None and record.revoked_at is None:
        record.revoked_at = utcnow()

    await audit.record(
        session,
        action=audit.ACTION_LOGOUT,
        actor_label=principal.label,
        actor_id=principal.user.id if principal.user else None,
        object_type="user",
        object_id=principal.id,
        source_ip=client_ip(request),
    )
    await session.commit()


@router.get("/me", response_model=CurrentUser)
async def me(principal: CurrentPrincipal) -> CurrentUser:
    if principal.user is None:
        raise AuthenticationError("endpoint is only available to user accounts")
    return CurrentUser.from_user(principal.user)


@router.post("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    payload: PasswordChange,
    request: Request,
    principal: CurrentPrincipal,
    session: DbSession,
) -> None:
    if principal.user is None:
        raise AuthenticationError("endpoint is only available to user accounts")
    user = principal.user

    if not verify_password(payload.current_password, user.password_hash):
        await audit.record(
            session,
            action="user.password_change",
            actor_label=user.email,
            actor_id=user.id,
            object_type="user",
            object_id=user.id,
            result=AuditResult.FAILURE,
            source_ip=client_ip(request),
        )
        await session.commit()
        raise AuthenticationError("current password is incorrect")

    user.password_hash = hash_password(payload.new_password)
    # Changing a password invalidates every existing session.
    await _revoke_family(session, user.id)

    await audit.record(
        session,
        action="user.password_change",
        actor_label=user.email,
        actor_id=user.id,
        object_type="user",
        object_id=user.id,
        source_ip=client_ip(request),
    )
    await session.commit()


@router.post("/edge/token", response_model=TokenPair)
async def edge_token(
    payload: EdgeTokenRequest,
    request: Request,
    session: DbSession,
) -> TokenPair:
    """Exchange an edge-node API key for a short-lived access token (PRD s18)."""
    settings = get_settings()
    node = (
        await session.execute(select(EdgeNode).where(EdgeNode.code == payload.node_code))
    ).scalar_one_or_none()

    digest = digest_token(payload.api_key)
    if node is None or not node.is_active or node.api_key_digest != digest:
        await audit.record(
            session,
            action=audit.ACTION_EDGE_TOKEN,
            actor_label=f"edge:{payload.node_code}",
            object_type="edge_node",
            object_id=node.id if node else None,
            result=AuditResult.FAILURE,
            source_ip=client_ip(request),
            context={"reason": "unknown node or invalid key"},
        )
        await session.commit()
        raise AuthenticationError("invalid edge node credentials")

    node.last_seen_at = utcnow()
    access_token, expires_at = create_access_token(
        node.id, (Role.EDGE_NODE.value,), node_id=node.code
    )

    await audit.record(
        session,
        action=audit.ACTION_EDGE_TOKEN,
        actor_label=f"edge:{node.code}",
        object_type="edge_node",
        object_id=node.id,
        source_ip=client_ip(request),
    )
    await session.commit()

    # No refresh token for machines: they hold a long-lived API key already, and
    # a second long-lived secret would only widen the attack surface.
    return TokenPair(
        access_token=access_token,
        refresh_token="",
        expires_at=expires_at,
        expires_in=settings.access_token_ttl_seconds,
    )


# --------------------------------------------------------------------------- #
# Administration
# --------------------------------------------------------------------------- #

admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.post(
    "/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require(Permission.USER_MANAGE))],
)
async def create_user(
    payload: UserCreate,
    request: Request,
    principal: CurrentPrincipal,
    session: DbSession,
) -> UserRead:
    email = payload.email.lower().strip()
    exists = (
        await session.execute(select(User.id).where(User.email == email))
    ).first()
    if exists:
        raise ConflictError("a user with this email already exists")

    user = User(
        email=email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        roles=[r.value for r in payload.roles],
        sector_scope=list(payload.sector_scope),
    )
    session.add(user)
    await session.flush()

    await audit.record(
        session,
        action=audit.ACTION_USER_CREATE,
        actor_label=principal.label,
        actor_id=principal.user.id if principal.user else None,
        object_type="user",
        object_id=user.id,
        source_ip=client_ip(request),
        context={"email": email, "roles": [r.value for r in payload.roles]},
    )
    await session.commit()
    return UserRead.model_validate(user)


@admin_router.get(
    "/users",
    response_model=list[UserRead],
    dependencies=[Depends(require(Permission.USER_MANAGE))],
)
async def list_users(session: DbSession) -> list[UserRead]:
    users = (await session.execute(select(User).order_by(User.email))).scalars()
    return [UserRead.model_validate(u) for u in users]


@admin_router.patch(
    "/users/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(require(Permission.USER_MANAGE))],
)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    request: Request,
    principal: CurrentPrincipal,
    session: DbSession,
) -> UserRead:
    user = (
        await session.execute(select(User).where(User.id == user_id))
    ).scalar_one_or_none()
    if user is None:
        raise NotFoundError("user not found")

    before = {
        "full_name": user.full_name,
        "roles": list(user.roles or ()),
        "is_active": user.is_active,
        "sector_scope": list(user.sector_scope or ()),
    }

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.roles is not None:
        user.roles = [r.value for r in payload.roles]
    if payload.is_active is not None:
        user.is_active = payload.is_active
        if not payload.is_active:
            # Deactivation must end active sessions immediately.
            await _revoke_family(session, user.id)
    if payload.sector_scope is not None:
        user.sector_scope = list(payload.sector_scope)

    after = {
        "full_name": user.full_name,
        "roles": list(user.roles or ()),
        "is_active": user.is_active,
        "sector_scope": list(user.sector_scope or ()),
    }

    await audit.record(
        session,
        action=audit.ACTION_USER_UPDATE,
        actor_label=principal.label,
        actor_id=principal.user.id if principal.user else None,
        object_type="user",
        object_id=user.id,
        source_ip=client_ip(request),
        context={"changes": audit.diff(before, after)},
    )
    await session.commit()
    return UserRead.model_validate(user)


@admin_router.post(
    "/edge-nodes",
    response_model=EdgeNodeCreated,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require(Permission.USER_MANAGE))],
)
async def create_edge_node(
    payload: EdgeNodeCreate,
    request: Request,
    principal: CurrentPrincipal,
    session: DbSession,
) -> EdgeNodeCreated:
    exists = (
        await session.execute(select(EdgeNode.id).where(EdgeNode.code == payload.code))
    ).first()
    if exists:
        raise ConflictError("an edge node with this code already exists")

    api_key, digest = generate_api_key()
    node = EdgeNode(
        code=payload.code,
        name=payload.name,
        site=payload.site,
        api_key_digest=digest,
    )
    session.add(node)
    await session.flush()

    await audit.record(
        session,
        action=audit.ACTION_EDGE_NODE_CREATE,
        actor_label=principal.label,
        actor_id=principal.user.id if principal.user else None,
        object_type="edge_node",
        object_id=node.id,
        source_ip=client_ip(request),
        context={"code": node.code},
    )
    await session.commit()

    # The plaintext key is returned exactly once; only its digest is stored.
    return EdgeNodeCreated(**_edge_node_fields(node), api_key=api_key)


def _edge_node_fields(node: EdgeNode) -> dict[str, object]:
    return {
        "id": node.id,
        "code": node.code,
        "name": node.name,
        "site": node.site,
        "is_active": node.is_active,
        "last_seen_at": node.last_seen_at,
        "last_sync_at": node.last_sync_at,
        "buffered_event_count": node.buffered_event_count,
        "agent_version": node.agent_version,
    }


async def _revoke_family(session: AsyncSession, user_id: object) -> None:
    """Revoke every live refresh token for a user."""
    tokens = (
        await session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None)
            )
        )
    ).scalars()
    now = utcnow()
    for token in tokens:
        token.revoked_at = now


@lru_cache(maxsize=1)
def _dummy_hash() -> str:
    """Argon2 hash of a fixed placeholder, computed once on first use.

    Verified against when the email is unknown so that a missing account and a
    wrong password cost comparable time. Without this the endpoint leaks which
    emails are registered.
    """
    return hash_password("timing-equalisation-placeholder-value")
