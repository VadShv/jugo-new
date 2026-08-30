from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal, require_permission
from jugo.modules.m6_scheduler import service
from jugo.modules.m6_scheduler.schemas import (
    CancelIn,
    FeedbackIn,
    InterviewCreate,
    InterviewOut,
    RescheduleIn,
    SlotOut,
)

router = APIRouter(prefix="/interviews", tags=["m6_scheduler"])


@router.get("/slots:suggest", response_model=list[SlotOut])
async def suggest_slots_endpoint(
    participants: list[uuid.UUID] = Query(default=[]),
    date_from: date | None = None,
    date_to: date | None = None,
    duration_min: int = 60,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("interview:read")),
) -> list[SlotOut]:
    await apply_rls(session, user)
    today = date.today()
    date_from = date_from or today
    date_to = date_to or date_from
    slots = await service.suggest(session, participants, date_from, date_to, duration_min)
    return [SlotOut(start=s) for s in slots]


@router.post("", response_model=InterviewOut)
async def create_interview(
    data: InterviewCreate,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("interview:write")),
) -> InterviewOut:
    await apply_rls(session, user)
    return await service.create_interview(session, data, user.user_id)


@router.post("/{interview_id}:reschedule", response_model=InterviewOut)
async def reschedule_interview(
    interview_id: uuid.UUID,
    data: RescheduleIn,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("interview:write")),
) -> InterviewOut:
    await apply_rls(session, user)
    return await service.reschedule(session, interview_id, data.scheduled_at, user.user_id)


@router.post("/{interview_id}:cancel", response_model=InterviewOut)
async def cancel_interview(
    interview_id: uuid.UUID,
    data: CancelIn,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("interview:write")),
) -> InterviewOut:
    await apply_rls(session, user)
    return await service.cancel(session, interview_id, data.reason, user.user_id)


@router.post("/{interview_id}:feedback", response_model=InterviewOut)
async def feedback_interview(
    interview_id: uuid.UUID,
    data: FeedbackIn,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("interview:write")),
) -> InterviewOut:
    await apply_rls(session, user)
    return await service.add_feedback(session, interview_id, data, user.user_id)


@router.get("/{interview_id}", response_model=InterviewOut)
async def get_interview(
    interview_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("interview:read")),
) -> InterviewOut:
    await apply_rls(session, user)
    return await service.get(session, interview_id)


@router.get("/vacancies/{vacancy_id}", response_model=list[InterviewOut])
async def list_interviews(
    vacancy_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("interview:read")),
) -> list[InterviewOut]:
    await apply_rls(session, user)
    return await service.list_for_vacancy(session, vacancy_id)
