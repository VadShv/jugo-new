from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def audit(
    session: AsyncSession,
    actor_id: uuid.UUID,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
    ip: str | None = None,
) -> None:
    await session.execute(
        text(
            """
            INSERT INTO audit_log
                (id, tenant_id, actor_id, action, entity_type, entity_id,
                 before, after, ip, created_at)
            VALUES
                (gen_random_uuid(),
                 current_setting('app.tenant_id')::uuid,
                 :actor_id, :action, :entity_type, :entity_id,
                 CAST(:before AS jsonb),
                 CAST(:after AS jsonb),
                 :ip,
                 now())
            """
        ),
        {
            "actor_id": str(actor_id),
            "action": action,
            "entity_type": entity_type,
            "entity_id": str(entity_id),
            "before": json.dumps(before, default=str) if before is not None else None,
            "after": json.dumps(after, default=str) if after is not None else None,
            "ip": ip,
        },
    )
