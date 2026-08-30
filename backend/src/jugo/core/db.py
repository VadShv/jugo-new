from __future__ import annotations

import base64
import contextvars
import json
import uuid
from collections.abc import AsyncIterator
from typing import Any, cast

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session

from jugo.core.config import get_settings

settings = get_settings()

_tenant_id_var: contextvars.ContextVar[uuid.UUID | None] = contextvars.ContextVar(
    "jugo_tenant_id", default=None
)

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
    _tenant_id_var.set(tenant_id)
    await session.execute(text(f"SET LOCAL app.tenant_id = '{tenant_id}'"))
    if user_id is not None:
        await session.execute(text(f"SET LOCAL app.user_id = '{user_id}'"))


@event.listens_for(Session, "before_flush")
def _fill_tenant_id(session: Session, _flush_context: Any, _instances: Any) -> None:
    tenant_id = _tenant_id_var.get()
    if tenant_id is None:
        return
    for obj in session.new:
        if getattr(obj, "tenant_id", None) is None:
            obj.tenant_id = tenant_id


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
