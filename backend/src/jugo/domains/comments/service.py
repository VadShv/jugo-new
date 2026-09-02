from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core import audit, outbox
from jugo.core.errors import ProblemException
from jugo.domains.comments.models import Comment
from jugo.domains.comments.schemas import CommentCreate, CommentOut, CommentUpdate


async def create(
    session: AsyncSession,
    application_id: uuid.UUID,
    author_id: uuid.UUID,
    data: CommentCreate,
) -> CommentOut:
    comment = Comment(
        application_id=application_id,
        author_id=author_id,
        parent_id=data.parent_id,
        body=data.body,
        is_private=data.is_private,
    )
    session.add(comment)
    await session.flush()
    await session.refresh(comment)
    await audit.audit(
        session,
        actor_id=author_id,
        action="comment.created",
        entity_type="comment",
        entity_id=comment.id,
        after={"application_id": str(application_id), "is_private": data.is_private},
    )
    await outbox.publish(
        session,
        event_type="comment.created",
        aggregate_type="application",
        aggregate_id=application_id,
        payload={"comment_id": str(comment.id), "is_private": data.is_private},
        actor=author_id,
    )
    return CommentOut.model_validate(comment)


async def list_by_application(session: AsyncSession, application_id: uuid.UUID) -> list[CommentOut]:
    result = await session.execute(
        select(Comment)
        .where(
            Comment.application_id == application_id,
            Comment.deleted_at.is_(None),
        )
        .order_by(Comment.created_at.asc())
    )
    return [CommentOut.model_validate(c) for c in result.scalars().all()]


async def update(
    session: AsyncSession,
    comment_id: uuid.UUID,
    author_id: uuid.UUID,
    data: CommentUpdate,
) -> CommentOut:
    result = await session.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if comment is None:
        raise ProblemException(404, "about:blank", "Comment not found", detail=str(comment_id))
    if comment.author_id != author_id:
        raise ProblemException(
            403, "about:blank", "Not the author", detail="Only the author can edit"
        )
    comment.body = data.body
    comment.updated_by = author_id
    await session.flush()
    await session.refresh(comment)
    await audit.audit(
        session,
        actor_id=author_id,
        action="comment.updated",
        entity_type="comment",
        entity_id=comment_id,
    )
    return CommentOut.model_validate(comment)


async def soft_delete(
    session: AsyncSession,
    comment_id: uuid.UUID,
    author_id: uuid.UUID,
) -> None:
    result = await session.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if comment is None:
        raise ProblemException(404, "about:blank", "Comment not found", detail=str(comment_id))
    if comment.author_id != author_id:
        raise ProblemException(
            403, "about:blank", "Not the author", detail="Only the author can delete"
        )
    from datetime import UTC, datetime

    comment.deleted_at = datetime.now(UTC)
    await session.flush()
    await audit.audit(
        session,
        actor_id=author_id,
        action="comment.deleted",
        entity_type="comment",
        entity_id=comment_id,
    )
