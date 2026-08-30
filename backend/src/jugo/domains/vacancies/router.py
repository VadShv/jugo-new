from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal, require_permission
from jugo.domains.vacancies import service
from jugo.domains.vacancies.schemas import (
    VacancyCreate,
    VacancyOut,
    VacancyPage,
    VacancyUpdate,
)

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.get("", response_model=VacancyPage)
async def list_vacancies(
    limit: int = Query(default=50, ge=1, le=200),
    cursor: str | None = Query(default=None),
    status: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("vacancy:read")),
) -> VacancyPage:
    await apply_rls(session, user)
    return await service.list(session, limit=limit, cursor=cursor, status=status)


@router.post("", response_model=VacancyOut, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    payload: VacancyCreate,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("vacancy:write")),
) -> VacancyOut:
    await apply_rls(session, user)
    return await service.create(session, payload)


@router.get("/{vacancy_id}", response_model=VacancyOut)
async def get_vacancy(
    vacancy_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("vacancy:read")),
) -> VacancyOut:
    await apply_rls(session, user)
    return await service.get(session, vacancy_id)


@router.patch("/{vacancy_id}", response_model=VacancyOut)
async def update_vacancy(
    vacancy_id: uuid.UUID,
    payload: VacancyUpdate,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("vacancy:write")),
) -> VacancyOut:
    await apply_rls(session, user)
    return await service.update(session, vacancy_id, payload)
