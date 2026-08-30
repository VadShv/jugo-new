from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal, require_permission
from jugo.modules.m4_searchmap import service
from jugo.modules.m4_searchmap.schemas import SearchMapOut

router = APIRouter(prefix="/search-map", tags=["m4_searchmap"])


@router.post("/vacancies/{vacancy_id}:generate", response_model=SearchMapOut)
async def generate_search_map(
    vacancy_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("searchmap:run")),
) -> SearchMapOut:
    await apply_rls(session, user)
    return await service.generate(session, vacancy_id, user.user_id)


@router.get("/vacancies/{vacancy_id}", response_model=SearchMapOut)
async def latest_search_map(
    vacancy_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("searchmap:read")),
) -> SearchMapOut:
    await apply_rls(session, user)
    return await service.get_latest(session, vacancy_id)


@router.get("/maps/{map_id}", response_model=SearchMapOut)
async def get_search_map(
    map_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("searchmap:read")),
) -> SearchMapOut:
    await apply_rls(session, user)
    return await service.get(session, map_id)
