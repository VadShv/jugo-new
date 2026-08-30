from __future__ import annotations

import uuid

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.domains.applications.models import Application
from jugo.domains.vacancies.models import Vacancy
from jugo.modules.m5_analytics.schemas import (
    AIStat,
    FunnelOut,
    RecruiterStat,
    SourceStat,
)


async def funnel(session: AsyncSession, vacancy_id: uuid.UUID) -> FunnelOut:
    status_rows = await session.execute(
        select(Application.status, func.count(Application.id))
        .where(Application.vacancy_id == vacancy_id)
        .group_by(Application.status)
    )
    by_status: dict[str, int] = {}
    for row in status_rows.all():
        status_val = str(row[0]) if row[0] is not None else "unknown"
        by_status[status_val] = int(row[1])

    stage_rows = await session.execute(
        select(Application.current_stage_id, func.count(Application.id))
        .where(Application.vacancy_id == vacancy_id)
        .group_by(Application.current_stage_id)
    )
    by_stage: list[dict[str, object]] = []
    for srow in stage_rows.all():
        by_stage.append(
            {"stage_id": str(srow[0]) if srow[0] is not None else None, "count": int(srow[1])}
        )

    total = sum(by_status.values())
    hired = by_status.get("hired", 0)
    rejected = by_status.get("rejected", 0)
    return FunnelOut(
        vacancy_id=vacancy_id,
        total=total,
        by_status=by_status,
        by_stage=by_stage,
        hired_rate=hired / total if total else 0.0,
        reject_rate=rejected / total if total else 0.0,
    )


async def sources(session: AsyncSession) -> list[SourceStat]:
    rows = await session.execute(
        select(Application.origin, func.count(Application.id)).group_by(Application.origin)
    )
    return [
        SourceStat(origin=str(row[0]) if row[0] is not None else "unknown", count=int(row[1]))
        for row in rows.all()
    ]


async def ai_stats(session: AsyncSession) -> list[AIStat]:
    rows = await session.execute(
        text(
            "SELECT task, COUNT(*) AS cnt, AVG(latency_ms) AS avg_lat "
            "FROM ai_runs WHERE tenant_id = current_setting('app.tenant_id')::uuid "
            "GROUP BY task ORDER BY cnt DESC"
        )
    )
    result: list[AIStat] = []
    for row in rows.all():
        avg_lat = row[2]
        result.append(
            AIStat(
                task=str(row[0]),
                count=int(row[1]),
                avg_latency_ms=float(avg_lat) if avg_lat is not None else None,
            )
        )
    return result


async def recruiters(session: AsyncSession) -> list[RecruiterStat]:
    rows = await session.execute(
        select(Vacancy.recruiter_id, func.count(Application.id))
        .join(Application, Application.vacancy_id == Vacancy.id)
        .group_by(Vacancy.recruiter_id)
    )
    return [RecruiterStat(recruiter_id=row[0], count=int(row[1])) for row in rows.all()]
