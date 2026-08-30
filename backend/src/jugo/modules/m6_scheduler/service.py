from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core import audit, outbox
from jugo.core.errors import ProblemException
from jugo.domains.applications.models import Application
from jugo.modules.m6_scheduler.models import M6AvailabilitySlot, M6Interview
from jugo.modules.m6_scheduler.schemas import (
    FeedbackIn,
    InterviewCreate,
    InterviewOut,
    Window,
)

WORK_START_MIN = 9 * 60
WORK_END_MIN = 18 * 60


def _to_minutes(hhmm: str) -> int:
    parts = hhmm.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def _from_minutes(total: int) -> str:
    return f"{total // 60:02d}:{total % 60:02d}"


def suggest_slots(
    windows: list[Window],
    date_from: date,
    date_to: date,
    duration_min: int = 60,
    buffer_min: int = 15,
    limit_per_day: int = 3,
) -> list[datetime]:
    by_dow: dict[int, tuple[int, int]] = {
        w.day_of_week: (_to_minutes(w.start), _to_minutes(w.end)) for w in windows
    }
    slots: list[datetime] = []
    current = date_from
    while current <= date_to:
        dow = current.weekday()
        if dow in by_dow:
            w_start, w_end = by_dow[dow]
            start = max(w_start, WORK_START_MIN)
            end = min(w_end, WORK_END_MIN)
            cursor = start
            count = 0
            while cursor + duration_min <= end and count < limit_per_day:
                slots.append(
                    datetime(current.year, current.month, current.day, cursor // 60, cursor % 60)
                )
                cursor += duration_min + buffer_min
                count += 1
        current += timedelta(days=1)
    return slots


def _intersect_windows(participant_windows: list[list[Window]]) -> list[Window]:
    if not participant_windows:
        return []
    n = len(participant_windows)
    by_dow: dict[int, list[tuple[int, int]]] = {}
    for windows in participant_windows:
        for w in windows:
            by_dow.setdefault(w.day_of_week, []).append((_to_minutes(w.start), _to_minutes(w.end)))
    result: list[Window] = []
    for dow, ranges in by_dow.items():
        if len(ranges) < n:
            continue
        start = max(r[0] for r in ranges)
        end = min(r[1] for r in ranges)
        if start < end:
            result.append(
                Window(day_of_week=dow, start=_from_minutes(start), end=_from_minutes(end))
            )
    return result


async def _load_windows(session: AsyncSession, participants: list[uuid.UUID]) -> list[list[Window]]:
    if not participants:
        return []
    result = await session.execute(
        select(M6AvailabilitySlot).where(
            M6AvailabilitySlot.user_id.in_(participants),
            M6AvailabilitySlot.is_block.is_(False),
        )
    )
    rows = result.scalars().all()
    by_user: dict[uuid.UUID, list[Window]] = {uid: [] for uid in participants}
    for row in rows:
        by_user.setdefault(row.user_id, []).append(
            Window(day_of_week=row.day_of_week, start=row.start_time, end=row.end_time)
        )
    return [by_user[uid] for uid in participants]


async def suggest(
    session: AsyncSession,
    participants: list[uuid.UUID],
    date_from: date,
    date_to: date,
    duration_min: int = 60,
) -> list[datetime]:
    participant_windows = await _load_windows(session, participants)
    common = _intersect_windows(participant_windows)
    return suggest_slots(common, date_from, date_to, duration_min=duration_min)


async def create_interview(
    session: AsyncSession, data: InterviewCreate, actor: uuid.UUID
) -> InterviewOut:
    app_result = await session.execute(
        select(Application).where(Application.id == data.application_id)
    )
    app = app_result.scalar_one_or_none()
    if app is None:
        raise ProblemException(
            404, "about:blank", "Application not found", detail=str(data.application_id)
        )
    interview = M6Interview(
        application_id=app.id,
        vacancy_id=app.vacancy_id,
        candidate_id=app.candidate_id,
        scheduled_at=data.scheduled_at,
        duration_min=data.duration_min,
        location=data.location,
        organizer_id=data.organizer_id,
        status="scheduled",
    )
    session.add(interview)
    await session.flush()
    await session.refresh(interview)
    await outbox.publish(
        session,
        event_type="interview.scheduled",
        aggregate_type="application",
        aggregate_id=app.id,
        payload={"interview_id": str(interview.id), "scheduled_at": data.scheduled_at.isoformat()},
        actor=actor,
    )
    await audit.audit(
        session,
        actor_id=actor,
        action="m6.interview.create",
        entity_type="m6_interview",
        entity_id=interview.id,
    )
    return InterviewOut.model_validate(interview)


async def _get(session: AsyncSession, interview_id: uuid.UUID) -> M6Interview:
    result = await session.execute(select(M6Interview).where(M6Interview.id == interview_id))
    interview = result.scalar_one_or_none()
    if interview is None:
        raise ProblemException(404, "about:blank", "Interview not found", detail=str(interview_id))
    return interview


async def reschedule(
    session: AsyncSession, interview_id: uuid.UUID, scheduled_at: datetime, actor: uuid.UUID
) -> InterviewOut:
    interview = await _get(session, interview_id)
    interview.scheduled_at = scheduled_at
    await session.flush()
    await outbox.publish(
        session,
        event_type="interview.scheduled",
        aggregate_type="m6_interview",
        aggregate_id=interview_id,
        payload={"scheduled_at": scheduled_at.isoformat(), "rescheduled": True},
        actor=actor,
    )
    await audit.audit(
        session,
        actor_id=actor,
        action="m6.interview.reschedule",
        entity_type="m6_interview",
        entity_id=interview_id,
    )
    return InterviewOut.model_validate(interview)


async def cancel(
    session: AsyncSession, interview_id: uuid.UUID, reason: str, actor: uuid.UUID
) -> InterviewOut:
    interview = await _get(session, interview_id)
    interview.status = "canceled"
    interview.cancel_reason = reason
    await session.flush()
    await outbox.publish(
        session,
        event_type="interview.canceled",
        aggregate_type="m6_interview",
        aggregate_id=interview_id,
        payload={"reason": reason},
        actor=actor,
    )
    await audit.audit(
        session,
        actor_id=actor,
        action="m6.interview.cancel",
        entity_type="m6_interview",
        entity_id=interview_id,
    )
    return InterviewOut.model_validate(interview)


async def add_feedback(
    session: AsyncSession, interview_id: uuid.UUID, data: FeedbackIn, actor: uuid.UUID
) -> InterviewOut:
    interview = await _get(session, interview_id)
    interview.feedback_decision = data.decision
    interview.feedback_notes = data.notes
    interview.feedback_per_question = data.per_question
    interview.status = "completed"
    await session.flush()
    await outbox.publish(
        session,
        event_type="interview.completed",
        aggregate_type="m6_interview",
        aggregate_id=interview_id,
        payload={"decision": data.decision},
        actor=actor,
    )
    await audit.audit(
        session,
        actor_id=actor,
        action="m6.interview.feedback",
        entity_type="m6_interview",
        entity_id=interview_id,
    )
    return InterviewOut.model_validate(interview)


async def get(session: AsyncSession, interview_id: uuid.UUID) -> InterviewOut:
    interview = await _get(session, interview_id)
    return InterviewOut.model_validate(interview)


async def list_for_vacancy(session: AsyncSession, vacancy_id: uuid.UUID) -> list[InterviewOut]:
    result = await session.execute(
        select(M6Interview)
        .where(M6Interview.vacancy_id == vacancy_id)
        .order_by(M6Interview.scheduled_at.asc())
    )
    return [InterviewOut.model_validate(i) for i in result.scalars().all()]
