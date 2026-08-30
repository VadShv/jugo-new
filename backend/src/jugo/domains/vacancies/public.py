from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal
from jugo.domains.vacancies import service
from jugo.domains.vacancies.schemas import (
    VacancyCreate,
    VacancyOut,
    VacancyPage,
    VacancyUpdate,
)


async def create_vacancy(
    session: AsyncSession, principal: UserPrincipal, data: VacancyCreate
) -> VacancyOut:
    await apply_rls(session, principal)
    return await service.create(session, data)


async def get_vacancy(
    session: AsyncSession, principal: UserPrincipal, vacancy_id: uuid.UUID
) -> VacancyOut:
    await apply_rls(session, principal)
    return await service.get(session, vacancy_id)


async def list_vacancies(
    session: AsyncSession,
    principal: UserPrincipal,
    limit: int = 50,
    cursor: str | None = None,
    status: str | None = None,
) -> VacancyPage:
    await apply_rls(session, principal)
    return await service.list(session, limit=limit, cursor=cursor, status=status)


async def update_vacancy(
    session: AsyncSession,
    principal: UserPrincipal,
    vacancy_id: uuid.UUID,
    data: VacancyUpdate,
) -> VacancyOut:
    await apply_rls(session, principal)
    return await service.update(session, vacancy_id, data)
