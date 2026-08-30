from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel


class FunnelOut(BaseModel):
    vacancy_id: uuid.UUID
    total: int
    by_status: dict[str, int]
    by_stage: list[dict[str, Any]]
    hired_rate: float
    reject_rate: float


class SourceStat(BaseModel):
    origin: str
    count: int


class AIStat(BaseModel):
    task: str
    count: int
    avg_latency_ms: float | None = None


class RecruiterStat(BaseModel):
    recruiter_id: uuid.UUID | None = None
    count: int
