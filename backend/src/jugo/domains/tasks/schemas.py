from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    due_at: datetime | None = None
    assignee_id: uuid.UUID | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    due_at: datetime | None = None
    assignee_id: uuid.UUID | None = None
    completed: bool | None = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    title: str
    description: str | None = None
    due_at: datetime | None = None
    assignee_id: uuid.UUID | None = None
    completed_at: datetime | None = None
    completed_by: uuid.UUID | None = None
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
