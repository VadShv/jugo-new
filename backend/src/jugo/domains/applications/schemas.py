from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApplicationCreate(BaseModel):
    candidate_id: uuid.UUID
    vacancy_id: uuid.UUID
    current_stage_id: uuid.UUID | None = None
    origin: str = Field(default="manual", max_length=32)
    status: str = Field(default="new", max_length=32)
    screening_score: float | None = Field(default=None, ge=0.0, le=1.0)
    risk_level: str | None = Field(default=None, max_length=16)
    owner_id: uuid.UUID | None = None
    salary_expectation: str | None = None


class ApplicationUpdate(BaseModel):
    current_stage_id: uuid.UUID | None = None
    origin: str | None = Field(default=None, max_length=32)
    status: str | None = Field(default=None, max_length=32)
    screening_score: float | None = Field(default=None, ge=0.0, le=1.0)
    risk_level: str | None = Field(default=None, max_length=16)
    owner_id: uuid.UUID | None = None
    salary_expectation: str | None = None
    next_action_at: datetime | None = None


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    candidate_id: uuid.UUID
    vacancy_id: uuid.UUID
    current_stage_id: uuid.UUID | None = None
    origin: str
    status: str
    screening_score: float | None = None
    risk_level: str | None = None
    version: int = 1
    stage_entered_at: datetime | None = None
    next_action_at: datetime | None = None
    owner_id: uuid.UUID | None = None
    salary_expectation: str | None = None
    rejection_reason_code: str | None = None
    rejection_comment: str | None = None
    created_at: datetime
    updated_at: datetime


class ApplicationPage(BaseModel):
    items: list[ApplicationOut]
    next_cursor: str | None = None
    has_more: bool = False


class ActivityOut(BaseModel):
    id: str
    type: str
    actor_id: uuid.UUID | None = None
    description: str
    metadata: dict[str, Any] | None = None
    created_at: datetime
