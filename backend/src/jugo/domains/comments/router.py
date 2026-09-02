from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal, require_permission
from jugo.domains.comments import service
from jugo.domains.comments.schemas import CommentCreate, CommentOut, CommentUpdate

router = APIRouter(tags=["comments"])


@router.post(
    "/applications/{application_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    application_id: uuid.UUID,
    payload: CommentCreate,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("comment:write")),
) -> CommentOut:
    await apply_rls(session, user)
    return await service.create(session, application_id, user.user_id, payload)


@router.get(
    "/applications/{application_id}/comments",
    response_model=list[CommentOut],
)
async def list_comments(
    application_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("comment:read")),
) -> list[CommentOut]:
    await apply_rls(session, user)
    return await service.list_by_application(session, application_id)


@router.patch("/comments/{comment_id}", response_model=CommentOut)
async def update_comment(
    comment_id: uuid.UUID,
    payload: CommentUpdate,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("comment:write")),
) -> CommentOut:
    await apply_rls(session, user)
    return await service.update(session, comment_id, user.user_id, payload)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("comment:write")),
) -> None:
    await apply_rls(session, user)
    await service.soft_delete(session, comment_id, user.user_id)
