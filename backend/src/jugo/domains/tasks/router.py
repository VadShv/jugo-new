from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import get_session
from jugo.core.rls import apply_rls
from jugo.core.security import UserPrincipal, require_permission
from jugo.domains.tasks import service
from jugo.domains.tasks.schemas import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(tags=["tasks"])


@router.post(
    "/applications/{application_id}/tasks",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    application_id: uuid.UUID,
    payload: TaskCreate,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("task:write")),
) -> TaskOut:
    await apply_rls(session, user)
    return await service.create(session, application_id, user.user_id, payload)


@router.get(
    "/applications/{application_id}/tasks",
    response_model=list[TaskOut],
)
async def list_tasks(
    application_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("task:read")),
) -> list[TaskOut]:
    await apply_rls(session, user)
    return await service.list_by_application(session, application_id)


@router.get("/tasks", response_model=list[TaskOut])
async def list_my_tasks(
    assignee_id: uuid.UUID | None = Query(default=None),
    incomplete: bool = Query(default=False),
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("task:read")),
) -> list[TaskOut]:
    await apply_rls(session, user)
    target = assignee_id or user.user_id
    return await service.list_by_assignee(session, target, incomplete_only=incomplete)


@router.patch("/tasks/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: uuid.UUID,
    payload: TaskUpdate,
    session: AsyncSession = Depends(get_session),
    user: UserPrincipal = Depends(require_permission("task:write")),
) -> TaskOut:
    await apply_rls(session, user)
    return await service.update(session, task_id, user.user_id, payload)
