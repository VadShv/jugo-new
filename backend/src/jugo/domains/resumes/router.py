from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal, require_permission
from jugo.domains.resumes.service import ResumeSourceOut, create_resume_source

router = APIRouter(prefix="/candidates", tags=["resumes"])


@router.post(
    "/{candidate_id}/resumes",
    response_model=ResumeSourceOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume(
    candidate_id: uuid.UUID,
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("resume:write")),
) -> ResumeSourceOut:
    await apply_rls(session, user)
    content = await file.read()
    return await create_resume_source(
        session,
        candidate_id=candidate_id,
        filename=file.filename or "unknown",
        mime_type=file.content_type or "application/octet-stream",
        size=len(content),
        content=content,
    )
