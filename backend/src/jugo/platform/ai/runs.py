from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def log_ai_run(session: AsyncSession, **fields: Any) -> None:
    await session.execute(
        text(
            """
            INSERT INTO ai_runs
                (id, tenant_id, task, provider, model, prompt_version,
                 input_payload, output, latency_ms, status, error, actor_id, created_at)
            VALUES
                (gen_random_uuid(),
                 current_setting('app.tenant_id')::uuid,
                 :task, :provider, :model, :prompt_version,
                 CAST(:input_payload AS jsonb),
                 CAST(:output AS jsonb),
                 :latency_ms, :status, :error,
                 CAST(:actor_id AS uuid),
                 now())
            """
        ),
        {
            "task": fields.get("task"),
            "provider": fields.get("provider"),
            "model": fields.get("model"),
            "prompt_version": fields.get("prompt_version"),
            "input_payload": json.dumps(fields.get("input_payload"), default=str),
            "output": json.dumps(fields.get("output"), default=str),
            "latency_ms": fields.get("latency_ms"),
            "status": fields.get("status", "ok"),
            "error": fields.get("error"),
            "actor_id": (
                str(fields["actor_id"])
                if isinstance(fields.get("actor_id"), uuid.UUID)
                else fields.get("actor_id")
            ),
        },
    )
