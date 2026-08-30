from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from jugo.core.models_base import Base, TenantMixin


class M2RiskReport(TenantMixin, Base):
    __tablename__ = "m2_risk_reports"

    application_id: Mapped[uuid.UUID] = mapped_column(index=True)
    candidate_id: Mapped[uuid.UUID] = mapped_column(index=True)
    vacancy_id: Mapped[uuid.UUID] = mapped_column(index=True)
    risk_level: Mapped[str | None] = mapped_column(String(16))
    signals: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB)
    top_risks: Mapped[list[str] | None] = mapped_column(JSONB)
    summary: Mapped[str | None] = mapped_column(Text)
    model: Mapped[str | None] = mapped_column(String(128))
    prompt_version: Mapped[int | None] = mapped_column()
    ai_run_id: Mapped[uuid.UUID | None] = mapped_column()
    status: Mapped[str] = mapped_column(String(32), default="completed")
