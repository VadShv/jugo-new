from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from jugo.core.models_base import Base, TenantMixin


class Vacancy(TenantMixin, Base):
    __tablename__ = "vacancies"

    title: Mapped[str] = mapped_column(String(512))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    headcount: Mapped[int] = mapped_column(Integer, default=1)
    recruiter_id: Mapped[uuid.UUID | None] = mapped_column()
    hiring_manager_id: Mapped[uuid.UUID | None] = mapped_column()


class VacancyRequirementSet(TenantMixin, Base):
    __tablename__ = "vacancy_requirement_sets"

    vacancy_id: Mapped[uuid.UUID] = mapped_column(index=True)
    version_no: Mapped[int] = mapped_column(Integer, default=1)
    origin: Mapped[str] = mapped_column(String(32), default="manual")
    criteria: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column()
    ai_run_id: Mapped[uuid.UUID | None] = mapped_column()
