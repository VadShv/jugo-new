from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from jugo.core.models_base import Base, TenantMixin


class M4SearchMap(TenantMixin, Base):
    __tablename__ = "m4_search_maps"

    vacancy_id: Mapped[uuid.UUID] = mapped_column(index=True)
    version_no: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    role_ontology: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    donors: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB)
    hypotheses: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB)
    anti_map: Mapped[list[str] | None] = mapped_column(JSONB)
    term_pool: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    query_passports: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB)
    justifications: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    model: Mapped[str | None] = mapped_column(String(128))
    prompt_version: Mapped[int | None] = mapped_column()
