from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal, require_permission
from jugo.domains.candidates import service
from jugo.domains.candidates.schemas import (
    CandidateCreate,
    CandidateOut,
    CandidatePage,
    CandidateUpdate,
)

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("", response_model=CandidatePage)
async def list_candidates(
    limit: int = Query(default=50, ge=1, le=200),
    cursor: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("candidate:read")),
) -> CandidatePage:
    await apply_rls(session, user)
    return await service.list(session, limit=limit, cursor=cursor)


@router.post("", response_model=CandidateOut, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    payload: CandidateCreate,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("candidate:write")),
) -> CandidateOut:
    await apply_rls(session, user)
    return await service.create(session, payload)


@router.get("/{candidate_id}", response_model=CandidateOut)
async def get_candidate(
    candidate_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("candidate:read")),
) -> CandidateOut:
    await apply_rls(session, user)
    return await service.get(session, candidate_id)


@router.patch("/{candidate_id}", response_model=CandidateOut)
async def update_candidate(
    candidate_id: uuid.UUID,
    payload: CandidateUpdate,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("candidate:write")),
) -> CandidateOut:
    await apply_rls(session, user)
    return await service.update(session, candidate_id, payload)
