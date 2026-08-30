from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FunnelPresetCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    is_default: bool = False


class FunnelPresetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: str | None = None
    is_default: bool
    created_at: datetime
    updated_at: datetime


class FunnelPresetPage(BaseModel):
    items: list[FunnelPresetOut]
    next_cursor: str | None = None
    has_more: bool = False


class FunnelStageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    preset_id: uuid.UUID | None = None
    vacancy_id: uuid.UUID | None = None
    name: str
    order_index: int
    stage_type: str
    created_at: datetime
    updated_at: datetime


class TransitionRequest(BaseModel):
    to_stage_id: uuid.UUID
    reason: str | None = None


class TransitionResult(BaseModel):
    application_id: uuid.UUID
    from_stage_id: uuid.UUID | None
    to_stage_id: uuid.UUID
    status: str
    transition_id: uuid.UUID
