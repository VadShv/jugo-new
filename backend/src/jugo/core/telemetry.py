from __future__ import annotations

import logging
from typing import Any

import structlog

_PII_KEYS = frozenset(
    {
        "password",
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "secret",
        "authorization",
        "ssn",
        "passport",
    }
)


def _redact_pii(_logger: Any, _method_name: Any, event_dict: dict[str, Any]) -> dict[str, Any]:
    for key in list(event_dict):
        if isinstance(key, str) and key.lower() in _PII_KEYS:
            event_dict[key] = "***REDACTED***"
    return event_dict


def configure_logging(env: str = "dev") -> structlog.stdlib.BoundLogger:
    logging.basicConfig(format="%(message)s", level=logging.INFO)

    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        _redact_pii,
    ]
    if env == "prod":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=False))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger("jugo")  # type: ignore[no-any-return]


def bind_request_context(tenant_id: str | None = None, trace_id: str | None = None) -> None:
    structlog.contextvars.clear_contextvars()
    if tenant_id is not None:
        structlog.contextvars.bind_contextvars(tenant_id=tenant_id)
    if trace_id is not None:
        structlog.contextvars.bind_contextvars(trace_id=trace_id)
