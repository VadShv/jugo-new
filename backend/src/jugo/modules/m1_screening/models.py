from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from jugo.core.models_base import Base, TenantMixin


class M1ScreeningResult(TenantMixin, Base):
    __tablename__ = "m1_screening_results"

    application_id: Mapped[uuid.UUID] = mapped_column(index=True)
    vacancy_id: Mapped[uuid.UUID] = mapped_column(index=True)
    candidate_id: Mapped[uuid.UUID] = mapped_column(index=True)
    requirement_set_id: Mapped[uuid.UUID | None] = mapped_column()
    total_score: Mapped[float | None] = mapped_column(Float)
    recommendation: Mapped[str | None] = mapped_column(String(32))
    confidence: Mapped[float | None] = mapped_column(Float)
    per_criterion: Mapped[list[dict[str, object]] | None] = mapped_column(JSONB)
    model: Mapped[str | None] = mapped_column(String(128))
    prompt_version: Mapped[int | None] = mapped_column()
    ai_run_id: Mapped[uuid.UUID | None] = mapped_column()
    status: Mapped[str] = mapped_column(String(32), default="completed")
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False)
