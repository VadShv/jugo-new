from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC
from typing import Any

import jwt
from fastapi import Depends, Header
from pydantic import BaseModel

from jugo.core.config import get_settings
from jugo.core.errors import ProblemException

settings = get_settings()

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "admin": ["*"],
    "recruiter": [
        "candidate:read",
        "candidate:write",
        "vacancy:read",
        "vacancy:write",
        "application:read",
        "application:write",
        "funnel:read",
        "funnel:write",
        "search:read",
        "resume:read",
        "resume:write",
        "file:read",
        "file:write",
        "organization:read",
        "organization:write",
        "screening:run",
        "screening:read",
    ],
    "hiring_manager": [
        "candidate:read",
        "vacancy:read",
        "application:read",
        "application:write",
        "funnel:read",
        "search:read",
        "resume:read",
        "organization:read",
        "screening:read",
    ],
    "viewer": [
        "candidate:read",
        "vacancy:read",
        "application:read",
        "funnel:read",
        "search:read",
        "organization:read",
        "screening:read",
    ],
}


class UserPrincipal(BaseModel):
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    role: str = "viewer"


def decode_jwt(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as exc:
        raise ProblemException(
            status=401,
            type_="about:blank",
            title="Invalid token",
            detail=str(exc),
        ) from exc


def _has_permission(role: str, permission: str) -> bool:
    perms = ROLE_PERMISSIONS.get(role, [])
    if "*" in perms:
        return True
    if permission in perms:
        return True
    resource = permission.split(":", 1)[0]
    return f"{resource}:*" in perms


async def current_user(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> UserPrincipal:
    if authorization is None or not authorization.lower().startswith("bearer "):
        raise ProblemException(
            status=401,
            type_="about:blank",
            title="Missing credentials",
            detail="Authorization Bearer header is required",
        )
    token = authorization.split(" ", 1)[1].strip()
    claims = decode_jwt(token)
    try:
        return UserPrincipal(
            user_id=uuid.UUID(str(claims["sub"])),
            tenant_id=uuid.UUID(str(claims["tenant_id"])),
            role=str(claims.get("role", "viewer")),
        )
    except (KeyError, ValueError) as exc:
        raise ProblemException(
            status=401,
            type_="about:blank",
            title="Invalid token claims",
            detail=str(exc),
        ) from exc


def require_permission(
    permission: str,
) -> Callable[..., Awaitable[UserPrincipal]]:
    async def _checker(user: UserPrincipal = Depends(current_user)) -> UserPrincipal:
        if not _has_permission(user.role, permission):
            raise ProblemException(
                status=403,
                type_="about:blank",
                title="Forbidden",
                detail=f"Permission denied: {permission}",
            )
        return user

    return _checker


def issue_token(user_id: uuid.UUID, tenant_id: uuid.UUID, role: str) -> str:
    from datetime import datetime, timedelta

    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_access_ttl_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
