from __future__ import annotations

import hashlib
from typing import Any

import httpx

from jugo.core.config import get_settings

_cache: dict[str, list[float]] = {}


def _key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def embed(texts: list[str]) -> list[list[float]]:
    settings = get_settings()
    keys = [_key(t) for t in texts]
    missing = [
        (i, t, k) for i, (t, k) in enumerate(zip(texts, keys, strict=True)) if k not in _cache
    ]
    if missing:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{settings.tei_url}/embed",
                json={"inputs": [t for _, t, _ in missing]},
            )
            resp.raise_for_status()
            data: Any = resp.json()
        for (idx, text, key), vec in zip(missing, data, strict=True):
            floats = [float(x) for x in vec]
            _cache[key] = floats
            _ = (idx, text)
    return [_cache[k] for k in keys]


def clear_cache() -> None:
    _cache.clear()
