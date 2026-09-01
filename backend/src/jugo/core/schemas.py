from __future__ import annotations

from pydantic import BaseModel


class JobAccepted(BaseModel):
    job_id: str | None = None
    status: str = "queued"
