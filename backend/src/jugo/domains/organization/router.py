from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import decode_cursor, encode_cursor, get_session
from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal, require_permission
from jugo.domains.organization.models import (
    LegalEntity,
    LegalEntityOut,
    LegalEntityPage,
    OrgUnit,
    OrgUnitCreate,
    OrgUnitOut,
    OrgUnitPage,
)

router = APIRouter(prefix="/organization", tags=["organization"])

DEFAULT_LIMIT = 50
MAX_LIMIT = 200


def _keyset(stmt: Any, cursor: str | None, updated_at_col: Any, id_col: Any) -> Any:
    if cursor:
        key = decode_cursor(cursor)
        ts = datetime.fromisoformat(key["updated_at"])
        cid = uuid.UUID(key["id"])
        stmt = stmt.where(
            or_(
                updated_at_col < ts,
                and_(updated_at_col == ts, id_col < cid),
            )
        )
    return stmt


@router.get("/units", response_model=OrgUnitPage)
async def list_org_units(
    limit: int = Query(default=50, ge=1, le=200),
    cursor: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("organization:read")),
) -> OrgUnitPage:
    await apply_rls(session, user)
    limit = max(1, min(limit, MAX_LIMIT))
    stmt = _keyset(
        select(OrgUnit).order_by(OrgUnit.updated_at.desc(), OrgUnit.id.desc()).limit(limit + 1),
        cursor,
        OrgUnit.updated_at,
        OrgUnit.id,
    )
    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    has_more = len(rows) > limit
    items = rows[:limit]
    next_cursor: str | None = None
    if has_more and items:
        last = items[-1]
        next_cursor = encode_cursor({"updated_at": last.updated_at.isoformat(), "id": str(last.id)})
    return OrgUnitPage(
        items=[OrgUnitOut.model_validate(o) for o in items],
        next_cursor=next_cursor,
        has_more=has_more,
    )


@router.post("/units", response_model=OrgUnitOut, status_code=status.HTTP_201_CREATED)
async def create_org_unit(
    payload: OrgUnitCreate,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("organization:write")),
) -> OrgUnitOut:
    await apply_rls(session, user)
    org_unit = OrgUnit(**payload.model_dump())
    session.add(org_unit)
    await session.flush()
    await session.refresh(org_unit)
    return OrgUnitOut.model_validate(org_unit)


@router.get("/legal-entities", response_model=LegalEntityPage)
async def list_legal_entities(
    limit: int = Query(default=50, ge=1, le=200),
    cursor: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("organization:read")),
) -> LegalEntityPage:
    await apply_rls(session, user)
    limit = max(1, min(limit, MAX_LIMIT))
    stmt = _keyset(
        select(LegalEntity)
        .order_by(LegalEntity.updated_at.desc(), LegalEntity.id.desc())
        .limit(limit + 1),
        cursor,
        LegalEntity.updated_at,
        LegalEntity.id,
    )
    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    has_more = len(rows) > limit
    items = rows[:limit]
    next_cursor: str | None = None
    if has_more and items:
        last = items[-1]
        next_cursor = encode_cursor({"updated_at": last.updated_at.isoformat(), "id": str(last.id)})
    return LegalEntityPage(
        items=[LegalEntityOut.model_validate(e) for e in items],
        next_cursor=next_cursor,
        has_more=has_more,
    )
