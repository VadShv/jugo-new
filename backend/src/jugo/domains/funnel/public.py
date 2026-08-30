from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal
from jugo.domains.funnel import service
from jugo.domains.funnel.schemas import (
    FunnelPresetCreate,
    FunnelPresetOut,
    FunnelPresetPage,
    TransitionResult,
)


async def create_preset(
    session: AsyncSession, principal: UserPrincipal, data: FunnelPresetCreate
) -> FunnelPresetOut:
    await apply_rls(session, principal)
    return await service.create_preset(session, data)


async def list_presets(
    session: AsyncSession,
    principal: UserPrincipal,
    limit: int = 50,
    cursor: str | None = None,
) -> FunnelPresetPage:
    await apply_rls(session, principal)
    return await service.list_presets(session, limit=limit, cursor=cursor)


async def transition(
    session: AsyncSession,
    principal: UserPrincipal,
    application_id: uuid.UUID,
    to_stage_id: uuid.UUID,
    reason: str | None = None,
) -> TransitionResult:
    await apply_rls(session, principal)
    return await service.transition(
        session,
        application_id=application_id,
        to_stage_id=to_stage_id,
        actor=principal.user_id,
        reason=reason,
    )
