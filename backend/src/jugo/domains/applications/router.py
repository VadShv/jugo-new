from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal, require_permission
from jugo.domains.applications import service
from jugo.domains.applications.schemas import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationPage,
    ApplicationUpdate,
)
from jugo.domains.funnel import service as funnel_service
from jugo.domains.funnel.schemas import TransitionRequest, TransitionResult

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=ApplicationPage)
async def list_applications(
    limit: int = Query(default=50, ge=1, le=200),
    cursor: str | None = Query(default=None),
    vacancy_id: uuid.UUID | None = Query(default=None),
    candidate_id: uuid.UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("application:read")),
) -> ApplicationPage:
    await apply_rls(session, user)
    return await service.list(
        session,
        limit=limit,
        cursor=cursor,
        vacancy_id=vacancy_id,
        candidate_id=candidate_id,
        status=status,
    )


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreate,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("application:write")),
) -> ApplicationOut:
    await apply_rls(session, user)
    return await service.create(session, payload)


@router.get("/{application_id}", response_model=ApplicationOut)
async def get_application(
    application_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("application:read")),
) -> ApplicationOut:
    await apply_rls(session, user)
    return await service.get(session, application_id)


@router.patch("/{application_id}", response_model=ApplicationOut)
async def update_application(
    application_id: uuid.UUID,
    payload: ApplicationUpdate,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("application:write")),
) -> ApplicationOut:
    await apply_rls(session, user)
    return await service.update(session, application_id, payload)


@router.post("/{application_id}/transition", response_model=TransitionResult)
async def transition_application(
    application_id: uuid.UUID,
    payload: TransitionRequest,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("application:write")),
) -> TransitionResult:
    await apply_rls(session, user)
    return await funnel_service.transition(
        session,
        application_id=application_id,
        to_stage_id=payload.to_stage_id,
        actor=user.user_id,
        reason=payload.reason,
        version=payload.version,
    )
