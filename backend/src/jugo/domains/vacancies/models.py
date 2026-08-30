from __future__ import annotations

import uuid

from sqlalchemy import Integer, String, Text
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
