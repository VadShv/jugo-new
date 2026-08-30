from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def publish(
    session: AsyncSession,
    event_type: str,
    aggregate_type: str,
    aggregate_id: uuid.UUID,
    payload: dict[str, Any],
    actor: uuid.UUID | None = None,
) -> None:
    await session.execute(
        text(
            """
            INSERT INTO outbox_events
                (id, tenant_id, event_type, aggregate_type, aggregate_id,
                 payload, actor_id, created_at)
            VALUES
                (gen_random_uuid(),
                 current_setting('app.tenant_id')::uuid,
                 :event_type, :aggregate_type, :aggregate_id,
                 CAST(:payload AS jsonb),
                 CAST(:actor AS uuid),
                 now())
            """
        ),
        {
            "event_type": event_type,
            "aggregate_type": aggregate_type,
            "aggregate_id": str(aggregate_id),
            "payload": json.dumps(payload, default=str),
            "actor": str(actor) if actor is not None else None,
        },
    )
