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
from jugo.modules.m3_questions import service
from jugo.modules.m3_questions.schemas import QuestionSetOut

router = APIRouter(prefix="/questions", tags=["m3_questions"])


@router.post("/vacancies/{vacancy_id}:generate", response_model=JobAccepted, status_code=202)
async def generate_questions(
    vacancy_id: uuid.UUID,
    application_id: uuid.UUID | None = None,
    user: UserPrincipal = Depends(require_permission("questions:run")),
) -> JobAccepted:
    app_arg = str(application_id) if application_id else ""
    try:
        job = await enqueue(
            "generate_questions",
            str(vacancy_id),
            app_arg,
            str(user.tenant_id),
            str(user.user_id),
        )
    except Exception as exc:
        raise ProblemException(503, "about:blank", "Queue unavailable", detail=str(exc)) from exc
    return JobAccepted(job_id=job.job_id if job else None)


@router.post("/sets/{set_id}:approve", response_model=QuestionSetOut)
async def approve_questions(
    set_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("questions:run")),
) -> QuestionSetOut:
    await apply_rls(session, user)
    return await service.approve(session, set_id, user.user_id)


@router.get("/vacancies/{vacancy_id}", response_model=QuestionSetOut)
async def latest_questions(
    vacancy_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("questions:read")),
) -> QuestionSetOut:
    await apply_rls(session, user)
    return await service.get_latest(session, vacancy_id)


@router.get("/sets/{set_id}", response_model=QuestionSetOut)
async def get_question_set(
    set_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("questions:read")),
) -> QuestionSetOut:
    await apply_rls(session, user)
    return await service.get(session, set_id)
