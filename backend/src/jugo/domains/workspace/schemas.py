from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StageWithCount(BaseModel):
    id: uuid.UUID
    name: str
    order_index: int
    stage_type: str
    count: int


class ApplicationWithCandidate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    candidate_id: uuid.UUID
    vacancy_id: uuid.UUID
    current_stage_id: uuid.UUID | None = None
    status: str
    screening_score: float | None = None
    risk_level: str | None = None
    version: int = 1
    stage_entered_at: datetime | None = None
    owner_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    candidate_name: str = ""
    candidate_headline: str | None = None


class WorkspaceSummary(BaseModel):
    total: int
    new: int
    active: int
    rejected: int
    hired: int


class WorkspaceOut(BaseModel):
    vacancy_id: uuid.UUID
    vacancy_title: str
    vacancy_status: str
    vacancy_headcount: int
    stages: list[StageWithCount]
    summary: WorkspaceSummary
    applications: list[ApplicationWithCandidate]
    has_more: bool
