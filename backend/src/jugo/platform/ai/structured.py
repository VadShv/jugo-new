from __future__ import annotations

import json
import re
from typing import Any, cast


def parse_json_lenient(text: str) -> dict[str, Any] | list[Any] | None:
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1).strip()
    try:
        return cast(dict[str, Any] | list[Any] | None, json.loads(cleaned))
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}|\[.*\]", cleaned, re.DOTALL)
        if match:
            try:
                return cast(dict[str, Any] | list[Any] | None, json.loads(match.group(0)))
            except json.JSONDecodeError:
                return None
        return None


def validate_or_default(
    data: dict[str, Any] | None, required: list[str], defaults: dict[str, Any]
) -> dict[str, Any]:
    if data is None:
        data = {}
    result = {**defaults, **data}
    missing = [k for k in required if k not in result or result[k] is None]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    return result


__all__ = ["parse_json_lenient", "validate_or_default"]
