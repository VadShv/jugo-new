from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import decode_cursor, encode_cursor
from jugo.core.errors import ProblemException
from jugo.domains.applications.models import Application
from jugo.domains.applications.schemas import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationPage,
    ApplicationUpdate,
)

DEFAULT_LIMIT = 50
MAX_LIMIT = 200


async def create(session: AsyncSession, data: ApplicationCreate) -> ApplicationOut:
    application = Application(**data.model_dump())
    session.add(application)
    await session.flush()
    await session.refresh(application)
    return ApplicationOut.model_validate(application)


async def get(session: AsyncSession, application_id: uuid.UUID) -> ApplicationOut:
    result = await session.execute(select(Application).where(Application.id == application_id))
    application = result.scalar_one_or_none()
    if application is None:
        raise ProblemException(
            status=404,
            type_="about:blank",
            title="Application not found",
            detail=str(application_id),
        )
    return ApplicationOut.model_validate(application)


async def list(
    session: AsyncSession,
    limit: int = DEFAULT_LIMIT,
    cursor: str | None = None,
    vacancy_id: uuid.UUID | None = None,
    candidate_id: uuid.UUID | None = None,
    status: str | None = None,
) -> ApplicationPage:
    limit = max(1, min(limit, MAX_LIMIT))
    stmt = (
        select(Application)
        .order_by(Application.updated_at.desc(), Application.id.desc())
        .limit(limit + 1)
    )
    if vacancy_id is not None:
        stmt = stmt.where(Application.vacancy_id == vacancy_id)
    if candidate_id is not None:
        stmt = stmt.where(Application.candidate_id == candidate_id)
    if status is not None:
        stmt = stmt.where(Application.status == status)
    if cursor:
        key = decode_cursor(cursor)
        ts = datetime.fromisoformat(key["updated_at"])
        cid = uuid.UUID(key["id"])
        stmt = stmt.where(
            or_(
                Application.updated_at < ts,
                and_(Application.updated_at == ts, Application.id < cid),
            )
        )
    result = await session.execute(stmt)
    rows = [*result.scalars().all()]
    has_more = len(rows) > limit
    items = rows[:limit]
    next_cursor: str | None = None
    if has_more and items:
        last = items[-1]
        next_cursor = encode_cursor({"updated_at": last.updated_at.isoformat(), "id": str(last.id)})
    return ApplicationPage(
        items=[ApplicationOut.model_validate(a) for a in items],
        next_cursor=next_cursor,
        has_more=has_more,
    )


async def update(
    session: AsyncSession, application_id: uuid.UUID, data: ApplicationUpdate
) -> ApplicationOut:
    result = await session.execute(select(Application).where(Application.id == application_id))
    application = result.scalar_one_or_none()
    if application is None:
        raise ProblemException(
            status=404,
            type_="about:blank",
            title="Application not found",
            detail=str(application_id),
        )
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(application, field, value)
    application.version += 1
    await session.flush()
    await session.refresh(application)
    return ApplicationOut.model_validate(application)
