from __future__ import annotations

import base64
import json
import uuid
from collections.abc import AsyncIterator
from typing import Any, cast

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from jugo.core.config import get_settings

settings = get_settings()

async_engine = create_async_engine(
    settings.postgres_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def set_tenant_context(
    session: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID | None = None
) -> None:
    await session.execute(text("SET LOCAL app.tenant_id = :t"), {"t": str(tenant_id)})
    if user_id is not None:
        await session.execute(text("SET LOCAL app.user_id = :u"), {"u": str(user_id)})


async def ping_db() -> bool:
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def encode_cursor(key: dict[str, Any]) -> str:
    raw = json.dumps(key, default=str, sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def decode_cursor(cursor: str) -> dict[str, Any]:
    raw = base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")
    return cast(dict[str, Any], json.loads(raw))
