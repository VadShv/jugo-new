from __future__ import annotations

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from jugo.core.config import get_settings
from jugo.core.models_base import Base, TenantMixin

_settings = get_settings()


class ResumeSource(TenantMixin, Base):
    __tablename__ = "resume_sources"

    candidate_id: Mapped[uuid.UUID] = mapped_column(index=True)
    source_type: Mapped[str] = mapped_column(String(32), default="upload")
    source_url: Mapped[str | None] = mapped_column(String(1024))
    original_filename: Mapped[str | None] = mapped_column(String(512))
    mime_type: Mapped[str | None] = mapped_column(String(128))
    size_bytes: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="pending")


class ResumeVersion(TenantMixin, Base):
    __tablename__ = "resume_versions"

    resume_source_id: Mapped[uuid.UUID] = mapped_column(index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    parsed_text: Mapped[str | None] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(_settings.embedding_dim))
    parsed_metadata: Mapped[dict[str, object] | None] = mapped_column(JSONB)
