from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import and_, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core import audit, outbox
from jugo.core.db import decode_cursor, encode_cursor
from jugo.core.errors import ProblemException
from jugo.domains.applications.models import Application, RejectReason
from jugo.domains.applications.schemas import (
    ActivityOut,
    ApplicationCreate,
    ApplicationOut,
    ApplicationPage,
    ApplicationUpdate,
    RejectReasonOut,
)

DEFAULT_LIMIT = 50
MAX_LIMIT = 200


async def create(session: AsyncSession, data: ApplicationCreate) -> ApplicationOut:
    application = Application(**data.model_dump())
    session.add(application)
    await session.flush()
    await session.refresh(application)
    return ApplicationOut.model_validate(application)


async def get(session: AsyncSession, application_id: uuid.UUID) -> ApplicationOut:
    result = await session.execute(select(Application).where(Application.id == application_id))
    application = result.scalar_one_or_none()
    if application is None:
        raise ProblemException(
            status=404,
            type_="about:blank",
            title="Application not found",
            detail=str(application_id),
        )
    return ApplicationOut.model_validate(application)


async def list_applications(
    session: AsyncSession,
    limit: int = DEFAULT_LIMIT,
    cursor: str | None = None,
    vacancy_id: uuid.UUID | None = None,
    candidate_id: uuid.UUID | None = None,
    status: str | None = None,
) -> ApplicationPage:
    limit = max(1, min(limit, MAX_LIMIT))
    stmt = (
        select(Application)
        .order_by(Application.updated_at.desc(), Application.id.desc())
        .limit(limit + 1)
    )
    if vacancy_id is not None:
        stmt = stmt.where(Application.vacancy_id == vacancy_id)
    if candidate_id is not None:
        stmt = stmt.where(Application.candidate_id == candidate_id)
    if status is not None:
        stmt = stmt.where(Application.status == status)
    if cursor:
        key = decode_cursor(cursor)
        ts = datetime.fromisoformat(key["updated_at"])
        cid = uuid.UUID(key["id"])
        stmt = stmt.where(
            or_(
                Application.updated_at < ts,
                and_(Application.updated_at == ts, Application.id < cid),
            )
        )
    result = await session.execute(stmt)
    rows = [*result.scalars().all()]
    has_more = len(rows) > limit
    items = rows[:limit]
    next_cursor: str | None = None
    if has_more and items:
        last = items[-1]
        next_cursor = encode_cursor({"updated_at": last.updated_at.isoformat(), "id": str(last.id)})
    return ApplicationPage(
        items=[ApplicationOut.model_validate(a) for a in items],
        next_cursor=next_cursor,
        has_more=has_more,
    )


async def update(
    session: AsyncSession, application_id: uuid.UUID, data: ApplicationUpdate
) -> ApplicationOut:
    result = await session.execute(select(Application).where(Application.id == application_id))
    application = result.scalar_one_or_none()
    if application is None:
        raise ProblemException(
            status=404,
            type_="about:blank",
            title="Application not found",
            detail=str(application_id),
        )
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(application, field, value)
    application.version += 1
    await session.flush()
    await session.refresh(application)
    return ApplicationOut.model_validate(application)


async def list_activities(
    session: AsyncSession, application_id: uuid.UUID, limit: int = 50
) -> list[ActivityOut]:
    query = text(
        """
        SELECT 'stage_changed' AS type, id::text, actor_id,
               COALESCE('Переход: ' || reason, 'Переход по воронке') AS description,
               jsonb_build_object(
                   'from_stage_id', from_stage_id,
                   'to_stage_id', to_stage_id
               ) AS metadata,
               created_at
        FROM stage_transitions WHERE application_id = :app_id
        UNION ALL
        SELECT
            CASE
                WHEN action LIKE 'm1.%' THEN 'screening'
                WHEN action LIKE 'm2.%' THEN 'risk'
                WHEN action LIKE 'm3.%' THEN 'questions'
                WHEN action LIKE 'm4.%' THEN 'searchmap'
                WHEN action LIKE 'm6.%' THEN 'interview'
                WHEN action = 'application.created' THEN 'created'
                WHEN action = 'application.updated' THEN 'updated'
                ELSE 'system'
            END AS type,
            id::text, actor_id,
            action AS description,
            "after" AS metadata,
            created_at
        FROM audit_log
        WHERE entity_type = 'application'
              AND entity_id = :app_id
              AND action != 'application.transition'
        ORDER BY created_at DESC
        LIMIT :limit
        """
    )
    result = await session.execute(query, {"app_id": str(application_id), "limit": limit})
    rows = result.mappings().all()
    activities: list[ActivityOut] = []
    for row in rows:
        metadata: dict[str, Any] | None = row["metadata"]
        if isinstance(metadata, str):
            metadata = json.loads(metadata) if metadata else None
        activities.append(
            ActivityOut(
                id=row["id"],
                type=row["type"],
                actor_id=row["actor_id"],
                description=row["description"],
                metadata=metadata,
                created_at=row["created_at"],
            )
        )
    return activities


async def reject(
    session: AsyncSession,
    application_id: uuid.UUID,
    reason_code: str,
    comment: str | None,
    actor: uuid.UUID,
) -> ApplicationOut:
    result = await session.execute(select(Application).where(Application.id == application_id))
    app = result.scalar_one_or_none()
    if app is None:
        raise ProblemException(
            404, "about:blank", "Application not found", detail=str(application_id)
        )
    app.status = "rejected"
    app.rejection_reason_code = reason_code
    app.rejection_comment = comment
    app.version += 1
    await session.flush()
    await session.refresh(app)
    await audit.audit(
        session,
        actor_id=actor,
        action="application.rejected",
        entity_type="application",
        entity_id=application_id,
        after={"reason_code": reason_code, "comment": comment},
    )
    await outbox.publish(
        session,
        event_type="application.rejected",
        aggregate_type="application",
        aggregate_id=application_id,
        payload={"reason_code": reason_code},
        actor=actor,
    )
    return ApplicationOut.model_validate(app)


async def restore(
    session: AsyncSession,
    application_id: uuid.UUID,
    actor: uuid.UUID,
) -> ApplicationOut:
    result = await session.execute(select(Application).where(Application.id == application_id))
    app = result.scalar_one_or_none()
    if app is None:
        raise ProblemException(
            404, "about:blank", "Application not found", detail=str(application_id)
        )
    app.status = "active"
    app.rejection_reason_code = None
    app.rejection_comment = None
    app.version += 1
    await session.flush()
    await session.refresh(app)
    await audit.audit(
        session,
        actor_id=actor,
        action="application.restored",
        entity_type="application",
        entity_id=application_id,
    )
    await outbox.publish(
        session,
        event_type="application.restored",
        aggregate_type="application",
        aggregate_id=application_id,
        payload={},
        actor=actor,
    )
    return ApplicationOut.model_validate(app)


async def list_reject_reasons(session: AsyncSession) -> list[RejectReasonOut]:
    result = await session.execute(
        select(RejectReason)
        .where(RejectReason.is_active.is_(True))
        .order_by(RejectReason.code.asc())
    )
    return [RejectReasonOut.model_validate(r) for r in result.scalars().all()]
