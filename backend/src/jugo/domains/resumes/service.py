from __future__ import annotations

import uuid
from datetime import datetime
from io import BytesIO

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.domains.resumes.models import ResumeSource, ResumeVersion

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
PDF_MIME = "application/pdf"


class ResumeSourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    candidate_id: uuid.UUID
    source_type: str
    source_url: str | None = None
    original_filename: str | None = None
    mime_type: str | None = None
    size_bytes: int | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class ResumeVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_source_id: uuid.UUID
    version: int
    parsed_text: str | None = None
    created_at: datetime
    updated_at: datetime


def extract_text(content: bytes, mime_type: str) -> str:
    if mime_type == PDF_MIME:
        import pdfplumber

        pages_text: list[str] = []
        with pdfplumber.open(BytesIO(content)) as pdf:
            for page in pdf.pages:
                txt = page.extract_text() or ""
                pages_text.append(str(txt))
        return "\n".join(pages_text)
    if "wordprocessingml" in mime_type:
        import docx

        document = docx.Document(BytesIO(content))
        return "\n".join(str(p.text) for p in document.paragraphs)
    return ""


async def create_resume_source(
    session: AsyncSession,
    candidate_id: uuid.UUID,
    filename: str,
    mime_type: str,
    size: int,
    content: bytes,
) -> ResumeSourceOut:
    source = ResumeSource(
        candidate_id=candidate_id,
        source_type="upload",
        original_filename=filename,
        mime_type=mime_type,
        size_bytes=size,
        status="parsed",
    )
    session.add(source)
    await session.flush()
    await session.refresh(source)

    parsed_text = extract_text(content, mime_type)
    version = ResumeVersion(
        resume_source_id=source.id,
        version=1,
        parsed_text=parsed_text,
    )
    session.add(version)
    await session.flush()
    await session.refresh(version)

    return ResumeSourceOut.model_validate(source)
