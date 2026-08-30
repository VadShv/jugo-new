from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal, require_permission
from jugo.modules.m3_questions import service
from jugo.modules.m3_questions.schemas import QuestionSetOut

router = APIRouter(prefix="/questions", tags=["m3_questions"])


@router.post("/vacancies/{vacancy_id}:generate", response_model=QuestionSetOut)
async def generate_questions(
    vacancy_id: uuid.UUID,
    application_id: uuid.UUID | None = None,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("questions:run")),
) -> QuestionSetOut:
    await apply_rls(session, user)
    return await service.generate(session, vacancy_id, user.user_id, application_id)


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
