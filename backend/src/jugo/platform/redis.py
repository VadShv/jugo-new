from __future__ import annotations

import redis.asyncio as aioredis

from jugo.core.config import get_settings

_client: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _client
    if _client is None:
        _client = aioredis.from_url(  # type: ignore[no-untyped-call]
            get_settings().redis_url, decode_responses=True
        )
    return _client
