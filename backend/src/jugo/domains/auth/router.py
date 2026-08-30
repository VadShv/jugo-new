from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from jugo.core.config import get_settings
from jugo.core.security import UserPrincipal, current_user, issue_token
from jugo.domains.auth.models import LoginRequest, LoginResponse, MeOut

router = APIRouter(prefix="/auth", tags=["auth"])

DEMO_TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest) -> LoginResponse:
    settings = get_settings()
    user_id = uuid.uuid5(uuid.NAMESPACE_DNS, payload.email)
    token = issue_token(user_id=user_id, tenant_id=DEMO_TENANT_ID, role=payload.role)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_access_ttl_minutes * 60,
    )


@router.get("/me", response_model=MeOut)
async def me(user: UserPrincipal = Depends(current_user)) -> MeOut:
    return MeOut(user_id=user.user_id, tenant_id=user.tenant_id, role=user.role)
