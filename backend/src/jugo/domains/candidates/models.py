from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from jugo.core.models_base import Base, TenantMixin


class Candidate(TenantMixin, Base):
    __tablename__ = "candidates"

    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255), index=True)
    headline: Mapped[str | None] = mapped_column(String(1024))
    current_company: Mapped[str | None] = mapped_column(String(255))
    grade: Mapped[str | None] = mapped_column(String(32))
    location: Mapped[str | None] = mapped_column(String(255))
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(128)), default=list)
    is_blacklisted: Mapped[bool] = mapped_column(Boolean, default=False)
