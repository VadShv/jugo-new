from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class Donor(BaseModel):
    name: str
    tier: int = 2
    rationale: str | None = None


class Hypothesis(BaseModel):
    text: str
    rationale: str | None = None


class QueryPassport(BaseModel):
    platform: str
    query: str
    terms: list[str] = []
    exclusions: list[str] = []
    rationale: str | None = None


class SearchMapOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vacancy_id: uuid.UUID
    version_no: int
    status: str
    role_ontology: dict[str, Any] | None = None
    donors: list[Donor] = []
    hypotheses: list[Hypothesis] = []
    anti_map: list[str] = []
    term_pool: dict[str, Any] | None = None
    query_passports: list[QueryPassport] = []
    justifications: dict[str, str] = {}
    model: str | None = None
    created_at: datetime
    updated_at: datetime
