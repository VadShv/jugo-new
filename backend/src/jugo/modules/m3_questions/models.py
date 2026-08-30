from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from jugo.core.models_base import Base, TenantMixin


class M3QuestionSet(TenantMixin, Base):
    __tablename__ = "m3_question_sets"

    vacancy_id: Mapped[uuid.UUID] = mapped_column(index=True)
    application_id: Mapped[uuid.UUID | None] = mapped_column(index=True)
    version_no: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    origin: Mapped[str] = mapped_column(String(32), default="ai")
    manual_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    questions: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    model: Mapped[str | None] = mapped_column(String(128))
    prompt_version: Mapped[int | None] = mapped_column()
    ai_run_id: Mapped[uuid.UUID | None] = mapped_column()
