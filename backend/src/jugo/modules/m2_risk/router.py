from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.errors import ProblemException
from jugo.core.rls import apply_rls
from jugo.core.schemas import JobAccepted
from jugo.core.security import UserPrincipal, require_permission
from jugo.jobs.queue import enqueue
from jugo.modules.m2_risk import service
from jugo.modules.m2_risk.schemas import RiskReportOut

router = APIRouter(prefix="/risk", tags=["m2_risk"])


@router.post("/applications/{application_id}:run", response_model=JobAccepted, status_code=202)
async def run_risk(
    application_id: uuid.UUID,
    user: UserPrincipal = Depends(require_permission("risk:run")),
) -> JobAccepted:
    try:
        job = await enqueue(
            "analyze_risk", str(application_id), str(user.tenant_id), str(user.user_id)
        )
    except Exception as exc:
        raise ProblemException(503, "about:blank", "Queue unavailable", detail=str(exc)) from exc
    return JobAccepted(job_id=job.job_id if job else None)


@router.get("/applications/{application_id}", response_model=RiskReportOut)
async def get_risk(
    application_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("signal:read")),
) -> RiskReportOut:
    await apply_rls(session, user)
    return await service.get_report(session, application_id)
