from __future__ import annotations

import logging
import uuid
from typing import Any

from jugo.core.db import AsyncSessionLocal, set_tenant_context
from jugo.jobs.queue import redis_settings
from jugo.modules.m1_screening import service as m1_service
from jugo.modules.m2_risk import service as m2_service
from jugo.modules.m3_questions import service as m3_service
from jugo.modules.m4_searchmap import service as m4_service

log = logging.getLogger("jugo.worker")


async def _run(tenant_id: str, user_id: str, label: str, coro_factory: Any) -> str:
    async with AsyncSessionLocal() as session:
        await set_tenant_context(session, uuid.UUID(tenant_id), uuid.UUID(user_id))
        try:
            result = await coro_factory(session)
            await session.commit()
            return str(result.id)
        except Exception:
            await session.rollback()
            log.exception("%s failed", label)
            raise


async def generate_requirements(
    ctx: dict[str, Any], vacancy_id: str, tenant_id: str, user_id: str
) -> str:
    return await _run(
        tenant_id,
        user_id,
        "generate_requirements",
        lambda s: m1_service.generate_requirements(s, uuid.UUID(vacancy_id), uuid.UUID(user_id)),
    )


async def screen_application(
    ctx: dict[str, Any], application_id: str, tenant_id: str, user_id: str
) -> str:
    return await _run(
        tenant_id,
        user_id,
        "screen_application",
        lambda s: m1_service.screen(s, uuid.UUID(application_id), uuid.UUID(user_id)),
    )


async def analyze_risk(
    ctx: dict[str, Any], application_id: str, tenant_id: str, user_id: str
) -> str:
    return await _run(
        tenant_id,
        user_id,
        "analyze_risk",
        lambda s: m2_service.analyze(s, uuid.UUID(application_id), uuid.UUID(user_id)),
    )


async def generate_questions(
    ctx: dict[str, Any],
    vacancy_id: str,
    application_id: str,
    tenant_id: str,
    user_id: str,
) -> str:
    app_uuid = uuid.UUID(application_id) if application_id else None
    return await _run(
        tenant_id,
        user_id,
        "generate_questions",
        lambda s: m3_service.generate(s, uuid.UUID(vacancy_id), uuid.UUID(user_id), app_uuid),
    )


async def generate_search_map(
    ctx: dict[str, Any], vacancy_id: str, tenant_id: str, user_id: str
) -> str:
    return await _run(
        tenant_id,
        user_id,
        "generate_search_map",
        lambda s: m4_service.generate(s, uuid.UUID(vacancy_id), uuid.UUID(user_id)),
    )


class WorkerSettings:
    functions = [
        generate_requirements,
        screen_application,
        analyze_risk,
        generate_questions,
        generate_search_map,
    ]
    redis_settings = redis_settings()
    max_tries = 3
