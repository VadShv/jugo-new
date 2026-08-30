from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, DateTime, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from jugo.core.models_base import Base, TenantMixin


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class LegalEntity(TenantMixin, Base):
    __tablename__ = "legal_entities"

    name: Mapped[str] = mapped_column(String(255))
    inn: Mapped[str | None] = mapped_column(String(32), index=True)
    kpp: Mapped[str | None] = mapped_column(String(32))
    address: Mapped[str | None] = mapped_column(String(1024))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)


class OrgUnit(TenantMixin, Base):
    __tablename__ = "org_units"

    name: Mapped[str] = mapped_column(String(255))
    parent_id: Mapped[uuid.UUID | None] = mapped_column(index=True)
    head_id: Mapped[uuid.UUID | None] = mapped_column(index=True)


class OrgUnitCreate(BaseModel):
    name: str = Field(..., max_length=255)
    parent_id: uuid.UUID | None = None
    head_id: uuid.UUID | None = None


class OrgUnitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    parent_id: uuid.UUID | None = None
    head_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class OrgUnitPage(BaseModel):
    items: list[OrgUnitOut]
    next_cursor: str | None = None
    has_more: bool = False


class LegalEntityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    inn: str | None = None
    kpp: str | None = None
    address: str | None = None
    is_default: bool
    created_at: datetime
    updated_at: datetime


class LegalEntityPage(BaseModel):
    items: list[LegalEntityOut]
    next_cursor: str | None = None
    has_more: bool = False
