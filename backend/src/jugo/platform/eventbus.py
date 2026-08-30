from __future__ import annotations

from typing import Any


class EventBusPublisher:
    async def publish(self, stream: str, event: dict[str, Any]) -> None:
        return None


class ConsumerBase:
    async def handle(self, event: dict[str, Any]) -> None:
        raise NotImplementedError


__all__ = ["EventBusPublisher", "ConsumerBase"]
