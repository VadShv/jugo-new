from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.errors import ProblemException
from jugo.core.rls import apply_rls
from jugo.core.schemas import JobAccepted
from jugo.core.security import UserPrincipal, require_permission
from jugo.jobs.queue import enqueue
from jugo.modules.m1_screening import service
from jugo.modules.m1_screening.schemas import RequirementSetOut, ScreeningResultOut

router = APIRouter(prefix="/screening", tags=["m1_screening"])


async def _enqueue(func: str, *args: uuid.UUID | str) -> JobAccepted:
    try:
        job = await enqueue(func, *(str(a) for a in args))
    except Exception as exc:
        raise ProblemException(503, "about:blank", "Queue unavailable", detail=str(exc)) from exc
    return JobAccepted(job_id=job.job_id if job else None)


@router.post(
    "/vacancies/{vacancy_id}/requirements:generate",
    response_model=JobAccepted,
    status_code=202,
)
async def generate_requirements(
    vacancy_id: uuid.UUID,
    user: UserPrincipal = Depends(require_permission("screening:run")),
) -> JobAccepted:
    return await _enqueue("generate_requirements", vacancy_id, user.tenant_id, user.user_id)


@router.post("/applications/{application_id}:run", response_model=JobAccepted, status_code=202)
async def run_screening(
    application_id: uuid.UUID,
    user: UserPrincipal = Depends(require_permission("screening:run")),
) -> JobAccepted:
    return await _enqueue("screen_application", application_id, user.tenant_id, user.user_id)


@router.get("/applications/{application_id}", response_model=ScreeningResultOut)
async def get_screening(
    application_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("screening:read")),
) -> ScreeningResultOut:
    await apply_rls(session, user)
    return await service.get_result(session, application_id)


@router.get("/vacancies/{vacancy_id}/requirements", response_model=RequirementSetOut)
async def get_requirements(
    vacancy_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("screening:read")),
) -> RequirementSetOut:
    await apply_rls(session, user)
    return await service.get_latest_requirements(session, vacancy_id)
