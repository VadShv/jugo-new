from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Header, Query, Request
from fastapi.responses import StreamingResponse

from jugo.core.errors import ProblemException
from jugo.core.security import UserPrincipal, principal_from_token
from jugo.platform.eventbus import STREAM
from jugo.platform.redis import get_redis

router = APIRouter(prefix="/events", tags=["events"])


async def _sse_user(
    token: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
) -> UserPrincipal:
    tok = token
    if not tok and authorization and authorization.lower().startswith("bearer "):
        tok = authorization[7:].strip()
    if not tok:
        raise ProblemException(
            status=401,
            type_="about:blank",
            title="Missing credentials",
            detail="token query param or Authorization Bearer required",
        )
    return principal_from_token(tok)


async def _event_generator(request: Request, tenant_id: str) -> AsyncIterator[str]:
    redis = get_redis()
    last_id = request.headers.get("Last-Event-ID") or "$"
    while True:
        if await request.is_disconnected():
            break
        try:
            resp = await redis.xread({STREAM: last_id}, block=10000, count=100)
        except Exception:
            await asyncio.sleep(1)
            continue
        if not resp:
            yield ": heartbeat\n\n"
            continue
        for _stream, messages in resp:
            for msg_id, fields in messages:
                last_id = msg_id
                raw = fields.get("event")
                if not raw:
                    continue
                try:
                    event = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if str(event.get("tenant_id")) != tenant_id:
                    continue
                yield (
                    f"id: {msg_id}\n"
                    f"event: {event.get('event_type', 'message')}\n"
                    f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                )


@router.get("/stream")
async def stream(
    request: Request,
    user: UserPrincipal = Depends(_sse_user),
) -> StreamingResponse:
    return StreamingResponse(
        _event_generator(request, str(user.tenant_id)),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
