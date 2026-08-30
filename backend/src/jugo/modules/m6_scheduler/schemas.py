from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class Window(BaseModel):
    day_of_week: int
    start: str
    end: str


class SlotOut(BaseModel):
    start: datetime


class InterviewCreate(BaseModel):
    application_id: uuid.UUID
    scheduled_at: datetime
    duration_min: int = 60
    location: str | None = None
    organizer_id: uuid.UUID | None = None


class RescheduleIn(BaseModel):
    scheduled_at: datetime


class CancelIn(BaseModel):
    reason: str


class FeedbackIn(BaseModel):
    decision: str
    notes: str | None = None
    per_question: list[dict[str, Any]] | None = None


class InterviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    vacancy_id: uuid.UUID
    candidate_id: uuid.UUID
    scheduled_at: datetime
    duration_min: int
    status: str
    location: str | None = None
    organizer_id: uuid.UUID | None = None
    feedback_decision: str | None = None
    feedback_notes: str | None = None
    feedback_per_question: list[dict[str, Any]] | None = None
    cancel_reason: str | None = None
    created_at: datetime
    updated_at: datetime


class AvailabilitySlotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    day_of_week: int
    start_time: str
    end_time: str
    is_block: bool
