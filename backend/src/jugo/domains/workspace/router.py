from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal, require_permission
from jugo.domains.workspace import service
from jugo.domains.workspace.schemas import WorkspaceOut

router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.get("/vacancies/{vacancy_id}", response_model=WorkspaceOut)
async def get_workspace(
    vacancy_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("vacancy:read")),
) -> WorkspaceOut:
    await apply_rls(session, user)
    return await service.get_workspace(session, vacancy_id, limit=limit)
