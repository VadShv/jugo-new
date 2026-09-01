from __future__ import annotations

from typing import Any

from arq import create_pool
from arq.connections import RedisSettings

from jugo.core.config import get_settings

_pool: Any = None


def redis_settings() -> RedisSettings:
    return RedisSettings.from_dsn(get_settings().redis_url)


async def get_pool() -> Any:
    global _pool
    if _pool is None:
        _pool = await create_pool(redis_settings())
    return _pool


async def enqueue(func: str, *args: Any) -> Any:
    pool = await get_pool()
    return await pool.enqueue_job(func, *args)
