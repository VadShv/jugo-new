from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import decode_cursor, encode_cursor
from jugo.core.errors import ProblemException
from jugo.domains.vacancies.models import Vacancy
from jugo.domains.vacancies.schemas import (
    VacancyCreate,
    VacancyOut,
    VacancyPage,
    VacancyUpdate,
)

DEFAULT_LIMIT = 50
MAX_LIMIT = 200


async def create(session: AsyncSession, data: VacancyCreate) -> VacancyOut:
    vacancy = Vacancy(**data.model_dump())
    session.add(vacancy)
    await session.flush()
    await session.refresh(vacancy)
    return VacancyOut.model_validate(vacancy)


async def get(session: AsyncSession, vacancy_id: uuid.UUID) -> VacancyOut:
    result = await session.execute(
        select(Vacancy).where(Vacancy.id == vacancy_id)
    )
    vacancy = result.scalar_one_or_none()
    if vacancy is None:
        raise ProblemException(
            status=404,
            type_="about:blank",
            title="Vacancy not found",
            detail=str(vacancy_id),
        )
    return VacancyOut.model_validate(vacancy)


async def list(
    session: AsyncSession,
    limit: int = DEFAULT_LIMIT,
    cursor: str | None = None,
    status: str | None = None,
) -> VacancyPage:
    limit = max(1, min(limit, MAX_LIMIT))
    stmt = (
        select(Vacancy)
        .order_by(Vacancy.updated_at.desc(), Vacancy.id.desc())
        .limit(limit + 1)
    )
    if status is not None:
        stmt = stmt.where(Vacancy.status == status)
    if cursor:
        key = decode_cursor(cursor)
        ts = datetime.fromisoformat(key["updated_at"])
        cid = uuid.UUID(key["id"])
        stmt = stmt.where(
            or_(
                Vacancy.updated_at < ts,
                and_(Vacancy.updated_at == ts, Vacancy.id < cid),
            )
        )
    result = await session.execute(stmt)
    rows = [*result.scalars().all()]
    has_more = len(rows) > limit
    items = rows[:limit]
    next_cursor: str | None = None
    if has_more and items:
        last = items[-1]
        next_cursor = encode_cursor(
            {"updated_at": last.updated_at.isoformat(), "id": str(last.id)}
        )
    return VacancyPage(
        items=[VacancyOut.model_validate(v) for v in items],
        next_cursor=next_cursor,
        has_more=has_more,
    )


async def update(
    session: AsyncSession, vacancy_id: uuid.UUID, data: VacancyUpdate
) -> VacancyOut:
    result = await session.execute(
        select(Vacancy).where(Vacancy.id == vacancy_id)
    )
    vacancy = result.scalar_one_or_none()
    if vacancy is None:
        raise ProblemException(
            status=404,
            type_="about:blank",
            title="Vacancy not found",
            detail=str(vacancy_id),
        )
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(vacancy, field, value)
    await session.flush()
    await session.refresh(vacancy)
    return VacancyOut.model_validate(vacancy)
