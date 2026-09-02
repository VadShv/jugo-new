from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.errors import ProblemException
from jugo.domains.applications.models import Application
from jugo.domains.candidates.models import Candidate
from jugo.domains.funnel.models import FunnelPreset, FunnelStage
from jugo.domains.vacancies.models import Vacancy
from jugo.domains.workspace.schemas import (
    ApplicationWithCandidate,
    StageWithCount,
    WorkspaceOut,
    WorkspaceSummary,
)


async def get_workspace(
    session: AsyncSession,
    vacancy_id: uuid.UUID,
    limit: int = 50,
) -> WorkspaceOut:
    vacancy_result = await session.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    vacancy = vacancy_result.scalar_one_or_none()
    if vacancy is None:
        raise ProblemException(404, "about:blank", "Vacancy not found", detail=str(vacancy_id))

    preset_result = await session.execute(
        select(FunnelPreset)
        .where(FunnelPreset.tenant_id == vacancy.tenant_id, FunnelPreset.is_default.is_(True))
        .limit(1)
    )
    preset = preset_result.scalar_one_or_none()
    if preset is None:
        preset_result = await session.execute(
            select(FunnelPreset)
            .where(FunnelPreset.tenant_id == vacancy.tenant_id)
            .order_by(FunnelPreset.created_at.asc())
            .limit(1)
        )
        preset = preset_result.scalar_one_or_none()

    stages: list[StageWithCount] = []
    if preset is not None:
        stage_result = await session.execute(
            select(FunnelStage)
            .where(FunnelStage.preset_id == preset.id)
            .order_by(FunnelStage.order_index.asc())
        )
        stage_rows = stage_result.scalars().all()

        count_result = await session.execute(
            select(Application.current_stage_id, func.count(Application.id))
            .where(Application.vacancy_id == vacancy_id)
            .group_by(Application.current_stage_id)
        )
        counts: dict[uuid.UUID | None, int] = {}
        for stage_id, cnt in count_result.all():
            counts[stage_id] = cnt

        for s in stage_rows:
            stages.append(
                StageWithCount(
                    id=s.id,
                    name=s.name,
                    order_index=s.order_index,
                    stage_type=s.stage_type,
                    count=counts.get(s.id, 0),
                )
            )

    summary_result = await session.execute(
        select(Application.status, func.count(Application.id))
        .where(Application.vacancy_id == vacancy_id)
        .group_by(Application.status)
    )
    status_counts: dict[str, int] = {}
    for status, cnt in summary_result.all():
        status_counts[status] = cnt

    summary = WorkspaceSummary(
        total=sum(status_counts.values()),
        new=status_counts.get("new", 0),
        active=status_counts.get("in_progress", 0) + status_counts.get("active", 0),
        rejected=status_counts.get("rejected", 0),
        hired=status_counts.get("hired", 0),
    )

    app_result = await session.execute(
        select(Application, Candidate)
        .join(Candidate, Candidate.id == Application.candidate_id)
        .where(Application.vacancy_id == vacancy_id)
        .order_by(Application.updated_at.desc())
        .limit(limit + 1)
    )
    rows = app_result.all()
    has_more = len(rows) > limit
    applications: list[ApplicationWithCandidate] = []
    for app, cand in rows[:limit]:
        applications.append(
            ApplicationWithCandidate(
                id=app.id,
                candidate_id=app.candidate_id,
                vacancy_id=app.vacancy_id,
                current_stage_id=app.current_stage_id,
                status=app.status,
                screening_score=app.screening_score,
                risk_level=app.risk_level,
                version=app.version,
                stage_entered_at=app.stage_entered_at,
                owner_id=app.owner_id,
                created_at=app.created_at,
                updated_at=app.updated_at,
                candidate_name=f"{cand.last_name} {cand.first_name}",
                candidate_headline=cand.headline,
            )
        )

    return WorkspaceOut(
        vacancy_id=vacancy.id,
        vacancy_title=vacancy.title,
        vacancy_status=vacancy.status,
        vacancy_headcount=vacancy.headcount,
        stages=stages,
        summary=summary,
        applications=applications,
        has_more=has_more,
    )
