from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from jugo.core.models_base import Base, TenantMixin


class FunnelPreset(TenantMixin, Base):
    __tablename__ = "funnel_presets"

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)


class FunnelStage(TenantMixin, Base):
    __tablename__ = "funnel_stages"

    preset_id: Mapped[uuid.UUID | None] = mapped_column(index=True)
    vacancy_id: Mapped[uuid.UUID | None] = mapped_column(index=True)
    name: Mapped[str] = mapped_column(String(255))
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    stage_type: Mapped[str] = mapped_column(String(64), default="screening")
