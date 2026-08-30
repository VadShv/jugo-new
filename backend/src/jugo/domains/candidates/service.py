from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import decode_cursor, encode_cursor
from jugo.core.errors import ProblemException
from jugo.domains.candidates.models import Candidate
from jugo.domains.candidates.schemas import (
    CandidateCreate,
    CandidateOut,
    CandidatePage,
    CandidateUpdate,
)

DEFAULT_LIMIT = 50
MAX_LIMIT = 200


async def create(session: AsyncSession, data: CandidateCreate) -> CandidateOut:
    candidate = Candidate(**data.model_dump())
    session.add(candidate)
    await session.flush()
    await session.refresh(candidate)
    return CandidateOut.model_validate(candidate)


async def get(session: AsyncSession, candidate_id: uuid.UUID) -> CandidateOut:
    result = await session.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    candidate = result.scalar_one_or_none()
    if candidate is None:
        raise ProblemException(
            status=404,
            type_="about:blank",
            title="Candidate not found",
            detail=str(candidate_id),
        )
    return CandidateOut.model_validate(candidate)


async def list(
    session: AsyncSession,
    limit: int = DEFAULT_LIMIT,
    cursor: str | None = None,
) -> CandidatePage:
    limit = max(1, min(limit, MAX_LIMIT))
    stmt = (
        select(Candidate)
        .order_by(Candidate.updated_at.desc(), Candidate.id.desc())
        .limit(limit + 1)
    )
    if cursor:
        key = decode_cursor(cursor)
        ts = datetime.fromisoformat(key["updated_at"])
        cid = uuid.UUID(key["id"])
        stmt = stmt.where(
            or_(
                Candidate.updated_at < ts,
                and_(Candidate.updated_at == ts, Candidate.id < cid),
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
    return CandidatePage(
        items=[CandidateOut.model_validate(c) for c in items],
        next_cursor=next_cursor,
        has_more=has_more,
    )


async def update(
    session: AsyncSession, candidate_id: uuid.UUID, data: CandidateUpdate
) -> CandidateOut:
    result = await session.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    candidate = result.scalar_one_or_none()
    if candidate is None:
        raise ProblemException(
            status=404,
            type_="about:blank",
            title="Candidate not found",
            detail=str(candidate_id),
        )
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(candidate, field, value)
    await session.flush()
    await session.refresh(candidate)
    return CandidateOut.model_validate(candidate)
