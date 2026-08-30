from __future__ import annotations

from fastapi import APIRouter, Depends

from jugo.core.security import UserPrincipal, require_permission
from jugo.domains.files.service import (
    PresignRequest,
    PresignResponse,
    presign_upload,
)

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/presign", response_model=PresignResponse)
async def presign(
    payload: PresignRequest,
    user: UserPrincipal = Depends(require_permission("file:write")),
) -> PresignResponse:
    url = await presign_upload(payload.key, payload.expires)
    return PresignResponse(url=url, key=payload.key, expires=payload.expires)
