from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class QuestionCard(BaseModel):
    block: str = ""
    question: str
    probes: list[str] = []
    listen_for: list[str] = []
    red_flags: list[str] = []
    source_quote: str | None = None
    indicator: str | None = None
    valid: bool = True
    validation_issues: list[str] = []


class QuestionSetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vacancy_id: uuid.UUID
    application_id: uuid.UUID | None = None
    version_no: int
    status: str
    origin: str
    manual_edited: bool
    questions: list[QuestionCard]
    model: str | None = None
    created_at: datetime
    updated_at: datetime
