from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import set_tenant_context
from jugo.core.security import UserPrincipal


async def apply_rls(session: AsyncSession, principal: UserPrincipal) -> None:
    await set_tenant_context(session, principal.tenant_id, principal.user_id)


__all__ = ["set_tenant_context", "apply_rls"]
