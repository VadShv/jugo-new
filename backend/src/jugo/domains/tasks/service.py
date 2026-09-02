from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core import audit, outbox
from jugo.core.errors import ProblemException
from jugo.domains.tasks.models import Task
from jugo.domains.tasks.schemas import TaskCreate, TaskOut, TaskUpdate


async def create(
    session: AsyncSession,
    application_id: uuid.UUID,
    created_by: uuid.UUID,
    data: TaskCreate,
) -> TaskOut:
    task = Task(
        application_id=application_id,
        title=data.title,
        description=data.description,
        due_at=data.due_at,
        assignee_id=data.assignee_id,
        created_by=created_by,
    )
    session.add(task)
    await session.flush()
    await session.refresh(task)
    await audit.audit(
        session,
        actor_id=created_by,
        action="task.created",
        entity_type="task",
        entity_id=task.id,
        after={"application_id": str(application_id), "title": data.title},
    )
    await outbox.publish(
        session,
        event_type="task.created",
        aggregate_type="application",
        aggregate_id=application_id,
        payload={"task_id": str(task.id), "title": data.title},
        actor=created_by,
    )
    return TaskOut.model_validate(task)


async def list_by_application(session: AsyncSession, application_id: uuid.UUID) -> list[TaskOut]:
    result = await session.execute(
        select(Task)
        .where(Task.application_id == application_id)
        .order_by(
            Task.completed_at.is_(None).desc(),
            Task.due_at.asc().nulls_last(),
            Task.created_at.desc(),
        )
    )
    return [TaskOut.model_validate(t) for t in result.scalars().all()]


async def list_by_assignee(
    session: AsyncSession,
    assignee_id: uuid.UUID,
    incomplete_only: bool = False,
) -> list[TaskOut]:
    stmt = select(Task).where(Task.assignee_id == assignee_id)
    if incomplete_only:
        stmt = stmt.where(Task.completed_at.is_(None))
    stmt = stmt.order_by(Task.due_at.asc().nulls_last(), Task.created_at.desc())
    result = await session.execute(stmt)
    return [TaskOut.model_validate(t) for t in result.scalars().all()]


async def update(
    session: AsyncSession,
    task_id: uuid.UUID,
    actor_id: uuid.UUID,
    data: TaskUpdate,
) -> TaskOut:
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise ProblemException(404, "about:blank", "Task not found", detail=str(task_id))

    completed_changed = False
    if data.completed is True and task.completed_at is None:
        task.completed_at = datetime.now(UTC)
        task.completed_by = actor_id
        completed_changed = True
    elif data.completed is False and task.completed_at is not None:
        task.completed_at = None
        task.completed_by = None
        completed_changed = True

    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.due_at is not None:
        task.due_at = data.due_at
    if data.assignee_id is not None:
        task.assignee_id = data.assignee_id

    await session.flush()
    await session.refresh(task)

    if completed_changed:
        action = "task.completed" if task.completed_at else "task.uncompleted"
        await audit.audit(
            session,
            actor_id=actor_id,
            action=action,
            entity_type="task",
            entity_id=task_id,
        )
        await outbox.publish(
            session,
            event_type=action,
            aggregate_type="task",
            aggregate_id=task_id,
            payload={"completed": task.completed_at is not None},
            actor=actor_id,
        )
    return TaskOut.model_validate(task)
