from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core import audit, outbox
from jugo.core.errors import ProblemException
from jugo.domains.applications.models import Application
from jugo.domains.candidates.models import Candidate
from jugo.domains.vacancies.models import Vacancy
from jugo.modules.m3_questions.models import M3QuestionSet
from jugo.modules.m3_questions.schemas import QuestionCard, QuestionSetOut
from jugo.platform.ai import runs
from jugo.platform.ai.gateway import ai
from jugo.platform.ai.structured import parse_json_lenient

STOP_WORDS: tuple[str, ...] = (
    "возраст",
    "пол",
    "национальность",
    "религия",
    "инвалидность",
    "семейное положение",
    "беременность",
    "раса",
    "ориентация",
    "место рождения",
)
OPEN_WORDS: tuple[str, ...] = (
    "почему",
    "как ",
    "расскажите",
    "опишите",
    "приведите",
    "каким образом",
    "что вы",
    "как вы",
    "в чем",
)
BEHAVIORAL_MARKERS: tuple[str, ...] = (
    "приведите пример",
    "расскажите о ситуации",
    "был ли случай",
    "опишите случай",
    "вспомните",
)


def check_stop_words(question: str) -> list[str]:
    lowered = question.lower()
    return [w for w in STOP_WORDS if w in lowered]


def check_open_ended(question: str) -> bool:
    lowered = question.lower()
    return any(w in lowered for w in OPEN_WORDS)


def check_personalized(question: str, candidate_name: str | None) -> bool:
    lowered = question.lower()
    if candidate_name and candidate_name.lower() in lowered:
        return True
    if any(m in lowered for m in BEHAVIORAL_MARKERS):
        return True
    return "вы" in lowered and any(w in lowered for w in OPEN_WORDS)


def validate_question(card: QuestionCard, candidate_name: str | None) -> QuestionCard:
    issues: list[str] = []
    stops = check_stop_words(card.question)
    if stops:
        issues.append("stop_words:" + ",".join(stops))
    if not check_open_ended(card.question):
        issues.append("not_open_ended")
    if not check_personalized(card.question, candidate_name):
        issues.append("not_personalized")
    card.valid = len(issues) == 0
    card.validation_issues = issues
    return card


def _build_cards(parsed: dict[str, Any], candidate_name: str | None) -> list[QuestionCard]:
    raw = parsed.get("questions", [])
    cards = [QuestionCard.model_validate(q) for q in raw if isinstance(q, dict)]
    return [validate_question(c, candidate_name) for c in cards]


def _has_stop_words(cards: list[QuestionCard]) -> bool:
    return any("stop_words" in issue for c in cards for issue in c.validation_issues)


async def _load_vacancy(session: AsyncSession, vacancy_id: uuid.UUID) -> Vacancy:
    result = await session.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    vacancy = result.scalar_one_or_none()
    if vacancy is None:
        raise ProblemException(404, "about:blank", "Vacancy not found", detail=str(vacancy_id))
    return vacancy


async def _candidate_name_for(session: AsyncSession, application_id: uuid.UUID) -> str | None:
    app_result = await session.execute(select(Application).where(Application.id == application_id))
    app = app_result.scalar_one_or_none()
    if app is None:
        return None
    cand_result = await session.execute(select(Candidate).where(Candidate.id == app.candidate_id))
    candidate = cand_result.scalar_one_or_none()
    if candidate is None:
        return None
    return f"{candidate.first_name} {candidate.last_name}"


async def generate(
    session: AsyncSession,
    vacancy_id: uuid.UUID,
    actor: uuid.UUID,
    application_id: uuid.UUID | None = None,
) -> QuestionSetOut:
    vacancy = await _load_vacancy(session, vacancy_id)
    candidate_name = (
        await _candidate_name_for(session, application_id) if application_id is not None else None
    )

    payload: dict[str, Any] = {
        "vacancy_title": vacancy.title,
        "vacancy_description": vacancy.description or "",
        "candidate_name": candidate_name or "",
    }
    result = await ai.complete("m3.questions.generate", payload)
    parsed = parse_json_lenient(result.text)
    if not isinstance(parsed, dict):
        raise ProblemException(
            502, "about:blank", "AI returned invalid questions", detail=result.text[:200]
        )
    cards = _build_cards(parsed, candidate_name)

    if _has_stop_words(cards):
        retry_payload = {
            **payload,
            "feedback": "Избегайте дискриминационных тем: " + ", ".join(STOP_WORDS),
        }
        result = await ai.complete("m3.questions.generate", retry_payload)
        parsed_retry = parse_json_lenient(result.text)
        if isinstance(parsed_retry, dict):
            cards = _build_cards(parsed_retry, candidate_name)

    latest_result = await session.execute(
        select(M3QuestionSet.version_no)
        .where(M3QuestionSet.vacancy_id == vacancy_id)
        .order_by(M3QuestionSet.version_no.desc())
        .limit(1)
    )
    latest = latest_result.scalar_one_or_none()
    next_version = (latest + 1) if latest else 1

    qset = M3QuestionSet(
        vacancy_id=vacancy_id,
        application_id=application_id,
        version_no=next_version,
        status="draft",
        origin="ai",
        questions=[c.model_dump() for c in cards],
        model=result.model,
        prompt_version=1,
    )
    session.add(qset)
    await session.flush()
    await session.refresh(qset)

    await runs.log_ai_run(
        session,
        task="m3.questions.generate",
        provider=result.provider,
        model=result.model,
        prompt_version=1,
        input_payload=payload,
        output={"questions": [c.model_dump() for c in cards]},
        latency_ms=result.latency_ms,
        status="ok",
        actor_id=actor,
    )
    await outbox.publish(
        session,
        event_type="questions.generated",
        aggregate_type="vacancy",
        aggregate_id=vacancy_id,
        payload={"set_id": str(qset.id), "version_no": next_version},
        actor=actor,
    )
    await audit.audit(
        session,
        actor_id=actor,
        action="m3.questions.generate",
        entity_type="vacancy",
        entity_id=vacancy_id,
        after={"set_id": str(qset.id), "count": len(cards)},
    )
    return QuestionSetOut.model_validate(qset)


async def approve(session: AsyncSession, set_id: uuid.UUID, actor: uuid.UUID) -> QuestionSetOut:
    result = await session.execute(select(M3QuestionSet).where(M3QuestionSet.id == set_id))
    qset = result.scalar_one_or_none()
    if qset is None:
        raise ProblemException(404, "about:blank", "Question set not found", detail=str(set_id))
    qset.status = "approved"
    await session.flush()
    await audit.audit(
        session,
        actor_id=actor,
        action="m3.questions.approve",
        entity_type="m3_question_set",
        entity_id=set_id,
        after={"status": "approved"},
    )
    return QuestionSetOut.model_validate(qset)


async def get_latest(session: AsyncSession, vacancy_id: uuid.UUID) -> QuestionSetOut:
    result = await session.execute(
        select(M3QuestionSet)
        .where(M3QuestionSet.vacancy_id == vacancy_id)
        .order_by(M3QuestionSet.version_no.desc())
        .limit(1)
    )
    qset = result.scalar_one_or_none()
    if qset is None:
        raise ProblemException(404, "about:blank", "Question set not found", detail=str(vacancy_id))
    return QuestionSetOut.model_validate(qset)


async def get(session: AsyncSession, set_id: uuid.UUID) -> QuestionSetOut:
    result = await session.execute(select(M3QuestionSet).where(M3QuestionSet.id == set_id))
    qset = result.scalar_one_or_none()
    if qset is None:
        raise ProblemException(404, "about:blank", "Question set not found", detail=str(set_id))
    return QuestionSetOut.model_validate(qset)
