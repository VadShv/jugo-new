from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


class ProblemException(Exception):
    def __init__(
        self,
        status: int,
        type_: str,
        title: str,
        detail: str | None = None,
        instance: str | None = None,
    ) -> None:
        self.status = status
        self.type = type_
        self.title = title
        self.detail = detail
        self.instance = instance
        super().__init__(title)


async def problem_exception_handler(request: Request, exc: ProblemException) -> JSONResponse:
    content: dict[str, object] = {
        "type": exc.type,
        "title": exc.title,
        "status": exc.status,
    }
    if exc.detail is not None:
        content["detail"] = exc.detail
    content["instance"] = exc.instance or request.url.path
    return JSONResponse(
        status_code=exc.status,
        content=content,
        media_type="application/problem+json",
    )
