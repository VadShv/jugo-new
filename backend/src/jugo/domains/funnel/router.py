from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal, require_permission
from jugo.domains.funnel import service
from jugo.domains.funnel.schemas import (
    FunnelPresetCreate,
    FunnelPresetOut,
    FunnelPresetPage,
    FunnelStageOut,
)

router = APIRouter(prefix="/funnel", tags=["funnel"])


@router.get("/presets", response_model=FunnelPresetPage)
async def list_presets(
    limit: int = Query(default=50, ge=1, le=200),
    cursor: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("funnel:read")),
) -> FunnelPresetPage:
    await apply_rls(session, user)
    return await service.list_presets(session, limit=limit, cursor=cursor)


@router.get("/presets/{preset_id}/stages", response_model=list[FunnelStageOut])
async def list_stages(
    preset_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("funnel:read")),
) -> list[FunnelStageOut]:
    await apply_rls(session, user)
    return await service.list_stages(session, preset_id)


@router.post("/presets", response_model=FunnelPresetOut, status_code=status.HTTP_201_CREATED)
async def create_preset(
    payload: FunnelPresetCreate,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("funnel:write")),
) -> FunnelPresetOut:
    await apply_rls(session, user)
    return await service.create_preset(session, payload)
