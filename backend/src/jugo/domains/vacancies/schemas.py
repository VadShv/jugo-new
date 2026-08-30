from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

VACANCY_STATUSES = {"draft", "open", "paused", "closed", "on_hold"}


class VacancyBase(BaseModel):
    title: str = Field(..., max_length=512)
    description: str | None = None
    status: str = Field(default="draft", max_length=32)
    headcount: int = Field(default=1, ge=1)
    recruiter_id: uuid.UUID | None = None
    hiring_manager_id: uuid.UUID | None = None


class VacancyCreate(VacancyBase):
    pass


class VacancyUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=512)
    description: str | None = None
    status: str | None = Field(default=None, max_length=32)
    headcount: int | None = Field(default=None, ge=1)
    recruiter_id: uuid.UUID | None = None
    hiring_manager_id: uuid.UUID | None = None


class VacancyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    title: str
    description: str | None = None
    status: str
    headcount: int
    recruiter_id: uuid.UUID | None = None
    hiring_manager_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class VacancyPage(BaseModel):
    items: list[VacancyOut]
    next_cursor: str | None = None
    has_more: bool = False
