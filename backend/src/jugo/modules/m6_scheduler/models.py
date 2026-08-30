from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from jugo.core.models_base import Base, TenantMixin


class M6Interview(TenantMixin, Base):
    __tablename__ = "m6_interviews"

    application_id: Mapped[uuid.UUID] = mapped_column(index=True)
    vacancy_id: Mapped[uuid.UUID] = mapped_column(index=True)
    candidate_id: Mapped[uuid.UUID] = mapped_column(index=True)
    scheduled_at: Mapped[datetime] = mapped_column(index=True)
    duration_min: Mapped[int] = mapped_column(Integer, default=60)
    status: Mapped[str] = mapped_column(String(32), default="scheduled", index=True)
    location: Mapped[str | None] = mapped_column(String(255))
    organizer_id: Mapped[uuid.UUID | None] = mapped_column()
    feedback_decision: Mapped[str | None] = mapped_column(String(32))
    feedback_notes: Mapped[str | None] = mapped_column(Text)
    feedback_per_question: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB)
    cancel_reason: Mapped[str | None] = mapped_column(Text)


class M6AvailabilitySlot(TenantMixin, Base):
    __tablename__ = "m6_availability_slots"

    user_id: Mapped[uuid.UUID] = mapped_column(index=True)
    day_of_week: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[str] = mapped_column(String(8))
    end_time: Mapped[str] = mapped_column(String(8))
    is_block: Mapped[bool] = mapped_column(Boolean, default=False)
