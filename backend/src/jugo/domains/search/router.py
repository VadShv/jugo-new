from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal, require_permission
from jugo.domains.search.service import SearchRequest, SearchResponse, search

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/{entity}", response_model=SearchResponse)
async def search_entity(
    entity: str,
    payload: SearchRequest,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("search:read")),
) -> SearchResponse:
    await apply_rls(session, user)
    return await search(session, entity, payload)
