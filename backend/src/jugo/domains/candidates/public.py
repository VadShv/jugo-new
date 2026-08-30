from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal
from jugo.domains.candidates import service
from jugo.domains.candidates.schemas import (
    CandidateCreate,
    CandidateOut,
    CandidatePage,
    CandidateUpdate,
)


async def create_candidate(
    session: AsyncSession, principal: UserPrincipal, data: CandidateCreate
) -> CandidateOut:
    await apply_rls(session, principal)
    return await service.create(session, data)


async def get_candidate(
    session: AsyncSession, principal: UserPrincipal, candidate_id: uuid.UUID
) -> CandidateOut:
    await apply_rls(session, principal)
    return await service.get(session, candidate_id)


async def list_candidates(
    session: AsyncSession,
    principal: UserPrincipal,
    limit: int = 50,
    cursor: str | None = None,
) -> CandidatePage:
    await apply_rls(session, principal)
    return await service.list(session, limit=limit, cursor=cursor)


async def update_candidate(
    session: AsyncSession,
    principal: UserPrincipal,
    candidate_id: uuid.UUID,
    data: CandidateUpdate,
) -> CandidateOut:
    await apply_rls(session, principal)
    return await service.update(session, candidate_id, data)
