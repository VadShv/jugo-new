from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core import audit, outbox
from jugo.core.db import decode_cursor, encode_cursor
from jugo.core.errors import ProblemException
from jugo.domains.applications.models import Application
from jugo.domains.funnel.models import FunnelPreset, FunnelStage
from jugo.domains.funnel.schemas import (
    FunnelPresetCreate,
    FunnelPresetOut,
    FunnelPresetPage,
    TransitionResult,
)

DEFAULT_LIMIT = 50
MAX_LIMIT = 200

_STATUS_PROJECTION: dict[str, str] = {
    "hired": "hired",
    "rejected": "rejected",
    "offer": "offer",
    "offer_accepted": "hired",
    "withdrawn": "withdrawn",
}


def _project_status(stage_type: str) -> str:
    return _STATUS_PROJECTION.get(stage_type, "in_progress")


async def create_preset(session: AsyncSession, data: FunnelPresetCreate) -> FunnelPresetOut:
    preset = FunnelPreset(**data.model_dump())
    session.add(preset)
    await session.flush()
    await session.refresh(preset)
    return FunnelPresetOut.model_validate(preset)


async def list_presets(
    session: AsyncSession,
    limit: int = DEFAULT_LIMIT,
    cursor: str | None = None,
) -> FunnelPresetPage:
    limit = max(1, min(limit, MAX_LIMIT))
    stmt = (
        select(FunnelPreset)
        .order_by(FunnelPreset.updated_at.desc(), FunnelPreset.id.desc())
        .limit(limit + 1)
    )
    if cursor:
        key = decode_cursor(cursor)
        ts = datetime.fromisoformat(key["updated_at"])
        cid = uuid.UUID(key["id"])
        stmt = stmt.where(
            (FunnelPreset.updated_at < ts)
            | ((FunnelPreset.updated_at == ts) & (FunnelPreset.id < cid))
        )
    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    has_more = len(rows) > limit
    items = rows[:limit]
    next_cursor: str | None = None
    if has_more and items:
        last = items[-1]
        next_cursor = encode_cursor({"updated_at": last.updated_at.isoformat(), "id": str(last.id)})
    return FunnelPresetPage(
        items=[FunnelPresetOut.model_validate(p) for p in items],
        next_cursor=next_cursor,
        has_more=has_more,
    )


async def transition(
    session: AsyncSession,
    application_id: uuid.UUID,
    to_stage_id: uuid.UUID,
    actor: uuid.UUID,
    reason: str | None = None,
) -> TransitionResult:
    app_result = await session.execute(select(Application).where(Application.id == application_id))
    app = app_result.scalar_one_or_none()
    if app is None:
        raise ProblemException(
            status=404,
            type_="about:blank",
            title="Application not found",
            detail=str(application_id),
        )
    if app.current_stage_id == to_stage_id:
        raise ProblemException(
            status=409,
            type_="about:blank",
            title="Already in stage",
            detail=f"Application {application_id} is already in stage {to_stage_id}",
        )

    stage_result = await session.execute(select(FunnelStage).where(FunnelStage.id == to_stage_id))
    stage = stage_result.scalar_one_or_none()
    if stage is None:
        raise ProblemException(
            status=404,
            type_="about:blank",
            title="Stage not found",
            detail=str(to_stage_id),
        )

    from_stage_id = app.current_stage_id
    before: dict[str, Any] = {
        "current_stage_id": str(from_stage_id) if from_stage_id else None,
        "status": app.status,
    }
    app.current_stage_id = to_stage_id
    app.status = _project_status(stage.stage_type)
    after: dict[str, Any] = {
        "current_stage_id": str(to_stage_id),
        "status": app.status,
    }

    transition_result = await session.execute(
        text(
            """
            INSERT INTO stage_transitions
                (id, tenant_id, application_id, from_stage_id, to_stage_id,
                 reason, actor_id, created_at)
            VALUES
                (gen_random_uuid(),
                 current_setting('app.tenant_id')::uuid,
                 :app_id, :from_id, :to_id, :reason,
                 CAST(:actor AS uuid), now())
            RETURNING id
            """
        ),
        {
            "app_id": str(application_id),
            "from_id": str(from_stage_id) if from_stage_id else None,
            "to_id": str(to_stage_id),
            "reason": reason,
            "actor": str(actor),
        },
    )
    transition_id = uuid.UUID(str(transition_result.scalar_one()))

    await outbox.publish(
        session,
        event_type="application.stage.changed",
        aggregate_type="application",
        aggregate_id=application_id,
        payload={
            "from_stage_id": str(from_stage_id) if from_stage_id else None,
            "to_stage_id": str(to_stage_id),
            "stage_type": stage.stage_type,
            "status": app.status,
            "reason": reason,
        },
        actor=actor,
    )
    await audit.audit(
        session,
        actor_id=actor,
        action="application.transition",
        entity_type="application",
        entity_id=application_id,
        before=before,
        after=after,
    )
    await session.flush()

    return TransitionResult(
        application_id=application_id,
        from_stage_id=from_stage_id,
        to_stage_id=to_stage_id,
        status=app.status,
        transition_id=transition_id,
    )
