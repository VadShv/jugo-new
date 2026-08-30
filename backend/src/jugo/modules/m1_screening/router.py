from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal, require_permission
from jugo.modules.m1_screening import service
from jugo.modules.m1_screening.schemas import RequirementSetOut, ScreeningResultOut

router = APIRouter(prefix="/screening", tags=["m1_screening"])


@router.post("/vacancies/{vacancy_id}/requirements:generate", response_model=RequirementSetOut)
async def generate_requirements(
    vacancy_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("screening:run")),
) -> RequirementSetOut:
    await apply_rls(session, user)
    return await service.generate_requirements(session, vacancy_id, user.user_id)


@router.post("/applications/{application_id}:run", response_model=ScreeningResultOut)
async def run_screening(
    application_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("screening:run")),
) -> ScreeningResultOut:
    await apply_rls(session, user)
    return await service.screen(session, application_id, user.user_id)


@router.get("/applications/{application_id}", response_model=ScreeningResultOut)
async def get_screening(
    application_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("screening:read")),
) -> ScreeningResultOut:
    await apply_rls(session, user)
    return await service.get_result(session, application_id)
