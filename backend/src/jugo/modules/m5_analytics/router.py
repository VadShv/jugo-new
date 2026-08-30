from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal, require_permission
from jugo.modules.m5_analytics import service
from jugo.modules.m5_analytics.schemas import (
    AIStat,
    FunnelOut,
    RecruiterStat,
    SourceStat,
)

router = APIRouter(prefix="/analytics", tags=["m5_analytics"])


@router.get("/funnel/{vacancy_id}", response_model=FunnelOut)
async def funnel(
    vacancy_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("analytics:read")),
) -> FunnelOut:
    await apply_rls(session, user)
    return await service.funnel(session, vacancy_id)


@router.get("/sources", response_model=list[SourceStat])
async def sources(
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("analytics:read")),
) -> list[SourceStat]:
    await apply_rls(session, user)
    return await service.sources(session)


@router.get("/ai", response_model=list[AIStat])
async def ai(
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("analytics:read")),
) -> list[AIStat]:
    await apply_rls(session, user)
    return await service.ai_stats(session)


@router.get("/recruiters", response_model=list[RecruiterStat])
async def recruiters(
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("analytics:read")),
) -> list[RecruiterStat]:
    await apply_rls(session, user)
    return await service.recruiters(session)
