from __future__ import annotations

import uuid

from sqlalchemy import Float, String
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
