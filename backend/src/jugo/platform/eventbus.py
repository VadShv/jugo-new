from __future__ import annotations

import json
from typing import Any

from jugo.platform.redis import get_redis

STREAM = "jugo:events"


class EventBusPublisher:
    """Publishes events to a Redis Stream (XADD)."""

    async def publish(self, stream: str, event: dict[str, Any]) -> str:
        redis = get_redis()
        msg_id = await redis.xadd(stream, {"event": json.dumps(event, default=str)})
        return str(msg_id)


class ConsumerBase:
    """Base for competing-consumer event handlers (used by arq workers, G7)."""

    async def handle(self, event: dict[str, Any]) -> None:
        raise NotImplementedError


publisher = EventBusPublisher()

__all__ = ["STREAM", "EventBusPublisher", "ConsumerBase", "publisher"]
