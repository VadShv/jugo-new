from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal, require_permission
from jugo.modules.m2_risk import service
from jugo.modules.m2_risk.schemas import RiskReportOut

router = APIRouter(prefix="/risk", tags=["m2_risk"])


@router.post("/applications/{application_id}:run", response_model=RiskReportOut)
async def run_risk(
    application_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("risk:run")),
) -> RiskReportOut:
    await apply_rls(session, user)
    return await service.analyze(session, application_id, user.user_id)


@router.get("/applications/{application_id}", response_model=RiskReportOut)
async def get_risk(
    application_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("signal:read")),
) -> RiskReportOut:
    await apply_rls(session, user)
    return await service.get_report(session, application_id)
