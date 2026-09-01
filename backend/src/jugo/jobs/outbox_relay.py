from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from sqlalchemy import text

from jugo.core.db import AsyncSessionLocal
from jugo.platform.eventbus import STREAM, publisher

log = logging.getLogger("jugo.outbox_relay")

_BATCH_SQL = text(
    "SELECT id, tenant_id, event_type, aggregate_type, aggregate_id, "
    "payload, actor_id, created_at "
    "FROM outbox_events WHERE relayed_at IS NULL "
    "ORDER BY created_at LIMIT 100 FOR UPDATE SKIP LOCKED"
)
_MARK_SQL = text("UPDATE outbox_events SET relayed_at = now() WHERE id = :id")


async def relay_batch() -> int:
    async with AsyncSessionLocal() as session:
        rows = (await session.execute(_BATCH_SQL)).mappings().all()
        count = 0
        for row in rows:
            payload: Any = row["payload"]
            if isinstance(payload, str):
                payload = json.loads(payload)
            event: dict[str, Any] = {
                "event_id": str(row["id"]),
                "event_type": row["event_type"],
                "schema_version": 1,
                "occurred_at": row["created_at"].isoformat() if row["created_at"] else None,
                "tenant_id": str(row["tenant_id"]),
                "actor": {"type": "user", "id": str(row["actor_id"])} if row["actor_id"] else None,
                "aggregate": {"type": row["aggregate_type"], "id": str(row["aggregate_id"])},
                "payload": payload,
            }
            await publisher.publish(STREAM, event)
            await session.execute(_MARK_SQL, {"id": str(row["id"])})
            count += 1
        await session.commit()
        return count


async def run_outbox_relay() -> None:
    """Drains outbox_events into the Redis Stream. Resilient: logs and retries."""
    log.info("outbox relay started")
    while True:
        try:
            await relay_batch()
        except Exception:
            log.exception("outbox relay error")
            await asyncio.sleep(2)
            continue
        await asyncio.sleep(1.0)


if __name__ == "__main__":
    asyncio.run(run_outbox_relay())
