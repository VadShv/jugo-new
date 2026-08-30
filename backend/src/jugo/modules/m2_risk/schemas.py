from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RiskSignal(BaseModel):
    code: str
    severity: str = "low"
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    evidence: str | None = None
    alternative_explanation: str | None = None
    verification_question: str | None = None


class RiskReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    candidate_id: uuid.UUID
    vacancy_id: uuid.UUID
    risk_level: str | None = None
    signals: list[RiskSignal] = []
    top_risks: list[str] = []
    summary: str | None = None
    model: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
