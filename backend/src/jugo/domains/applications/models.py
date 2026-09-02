from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from jugo.core.models_base import Base, TenantMixin


class Application(TenantMixin, Base):
    __tablename__ = "applications"

    candidate_id: Mapped[uuid.UUID] = mapped_column(index=True)
    vacancy_id: Mapped[uuid.UUID] = mapped_column(index=True)
    current_stage_id: Mapped[uuid.UUID | None] = mapped_column(index=True)
    origin: Mapped[str] = mapped_column(String(32), default="manual")
    status: Mapped[str] = mapped_column(String(32), default="new", index=True)
    screening_score: Mapped[float | None] = mapped_column(Float)
    risk_level: Mapped[str | None] = mapped_column(String(16))
    version: Mapped[int] = mapped_column(Integer, default=1)
    stage_entered_at: Mapped[datetime | None] = mapped_column()
    next_action_at: Mapped[datetime | None] = mapped_column()
    owner_id: Mapped[uuid.UUID | None] = mapped_column(index=True)
    salary_expectation: Mapped[str | None] = mapped_column(Text)
    rejection_reason_code: Mapped[str | None] = mapped_column(String(64))
    rejection_comment: Mapped[str | None] = mapped_column(Text)


class RejectReason(TenantMixin, Base):
    __tablename__ = "reject_reasons"

    code: Mapped[str] = mapped_column(String(64))
    label: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
