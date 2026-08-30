from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Criterion(BaseModel):
    criterion: str
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    description: str | None = None


class RequirementSetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vacancy_id: uuid.UUID
    version_no: int
    origin: str
    criteria: list[Criterion]
    is_active: bool
    created_at: datetime


class CriterionScore(BaseModel):
    criterion: str
    score: float = Field(ge=0.0, le=1.0)
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence: str | None = None
    quote: str | None = None


class ScreeningResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    vacancy_id: uuid.UUID
    candidate_id: uuid.UUID
    requirement_set_id: uuid.UUID | None = None
    total_score: float | None = None
    recommendation: str | None = None
    confidence: float | None = None
    per_criterion: list[CriterionScore] | None = None
    model: str | None = None
    status: str
    is_stale: bool = False
    created_at: datetime
    updated_at: datetime
