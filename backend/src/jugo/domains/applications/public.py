from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal
from jugo.domains.applications import service
from jugo.domains.applications.schemas import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationPage,
    ApplicationUpdate,
)
from jugo.domains.funnel import service as funnel_service
from jugo.domains.funnel.schemas import TransitionResult


async def create_application(
    session: AsyncSession, principal: UserPrincipal, data: ApplicationCreate
) -> ApplicationOut:
    await apply_rls(session, principal)
    return await service.create(session, data)


async def get_application(
    session: AsyncSession, principal: UserPrincipal, application_id: uuid.UUID
) -> ApplicationOut:
    await apply_rls(session, principal)
    return await service.get(session, application_id)


async def list_applications(
    session: AsyncSession,
    principal: UserPrincipal,
    limit: int = 50,
    cursor: str | None = None,
    vacancy_id: uuid.UUID | None = None,
    candidate_id: uuid.UUID | None = None,
    status: str | None = None,
) -> ApplicationPage:
    await apply_rls(session, principal)
    return await service.list(
        session,
        limit=limit,
        cursor=cursor,
        vacancy_id=vacancy_id,
        candidate_id=candidate_id,
        status=status,
    )


async def update_application(
    session: AsyncSession,
    principal: UserPrincipal,
    application_id: uuid.UUID,
    data: ApplicationUpdate,
) -> ApplicationOut:
    await apply_rls(session, principal)
    return await service.update(session, application_id, data)


async def transition(
    session: AsyncSession,
    principal: UserPrincipal,
    application_id: uuid.UUID,
    to_stage_id: uuid.UUID,
    reason: str | None = None,
) -> TransitionResult:
    await apply_rls(session, principal)
    return await funnel_service.transition(
        session,
        application_id=application_id,
        to_stage_id=to_stage_id,
        actor=principal.user_id,
        reason=reason,
    )
