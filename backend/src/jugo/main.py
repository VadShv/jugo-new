from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from jugo.api import api_router
from jugo.core.config import get_settings
from jugo.core.errors import ProblemException, problem_exception_handler
from jugo.core.telemetry import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(env=settings.app_env)
    app = FastAPI(
        title="ATS Jugo",
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/api/v1/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if not settings.is_prod else [],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    app.add_exception_handler(ProblemException, problem_exception_handler)  # type: ignore[arg-type]
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/live", tags=["health"])
    async def live() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/ready", tags=["health"])
    async def ready() -> dict[str, str]:
        from jugo.core.db import async_engine

        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready"}

    return app


def main() -> None:
    import uvicorn

    logging.basicConfig(level=logging.INFO)
    uvicorn.run("jugo.main:create_app", factory=True, host="0.0.0.0", port=8000)


app = create_app()
