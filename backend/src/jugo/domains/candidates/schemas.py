from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CandidateBase(BaseModel):
    first_name: str = Field(..., max_length=255)
    last_name: str = Field(..., max_length=255)
    headline: str | None = Field(default=None, max_length=1024)
    current_company: str | None = Field(default=None, max_length=255)
    grade: str | None = Field(default=None, max_length=32)
    location: str | None = Field(default=None, max_length=255)
    tags: list[str] = Field(default_factory=list)
    is_blacklisted: bool = False


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    headline: str | None = Field(default=None, max_length=1024)
    current_company: str | None = Field(default=None, max_length=255)
    grade: str | None = Field(default=None, max_length=32)
    location: str | None = Field(default=None, max_length=255)
    tags: list[str] | None = None
    is_blacklisted: bool | None = None


class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    first_name: str
    last_name: str
    headline: str | None = None
    current_company: str | None = None
    grade: str | None = None
    location: str | None = None
    tags: list[str] = Field(default_factory=list)
    is_blacklisted: bool = False
    created_at: datetime
    updated_at: datetime


class CandidatePage(BaseModel):
    items: list[CandidateOut]
    next_cursor: str | None = None
    has_more: bool = False
