from __future__ import annotations

import json
import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core import audit, outbox
from jugo.core.errors import ProblemException
from jugo.domains.applications.models import Application
from jugo.domains.candidates.models import Candidate
from jugo.domains.resumes.models import ResumeSource, ResumeVersion
from jugo.domains.vacancies.models import Vacancy, VacancyRequirementSet
from jugo.modules.m1_screening.models import M1ScreeningResult
from jugo.modules.m1_screening.schemas import (
    Criterion,
    CriterionScore,
    RequirementSetOut,
    ScreeningResultOut,
)
from jugo.platform.ai import runs
from jugo.platform.ai.gateway import ai
from jugo.platform.ai.structured import parse_json_lenient


async def _load_vacancy(session: AsyncSession, vacancy_id: uuid.UUID) -> Vacancy:
    result = await session.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    vacancy = result.scalar_one_or_none()
    if vacancy is None:
        raise ProblemException(
            404, "about:blank", "Vacancy not found", detail=str(vacancy_id)
        )
    return vacancy


async def _latest_resume_text(
    session: AsyncSession, candidate_id: uuid.UUID
) -> str:
    result = await session.execute(
        select(ResumeVersion.parsed_text)
        .join(ResumeSource, ResumeSource.id == ResumeVersion.resume_source_id)
        .where(ResumeSource.candidate_id == candidate_id)
        .order_by(ResumeVersion.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none() or ""


async def generate_requirements(
    session: AsyncSession, vacancy_id: uuid.UUID, actor: uuid.UUID
) -> RequirementSetOut:
    vacancy = await _load_vacancy(session, vacancy_id)
    payload = {
        "vacancy_title": vacancy.title,
        "vacancy_description": vacancy.description or "",
    }
    result = await ai.complete("m1.criteria.generate", payload)
    parsed = parse_json_lenient(result.text)
    if not isinstance(parsed, list):
        raise ProblemException(
            502, "about:blank", "AI returned invalid criteria", detail=result.text[:200]
        )
    criteria = [Criterion.model_validate(item) for item in parsed]

    await session.execute(
        update(VacancyRequirementSet)
        .where(VacancyRequirementSet.vacancy_id == vacancy_id)
        .values(is_active=False)
    )

    req_set = VacancyRequirementSet(
        vacancy_id=vacancy_id,
        name="AI criteria",
        requirements=[c.model_dump() for c in criteria],
        is_active=True,
    )
    session.add(req_set)
    await session.flush()
    await session.refresh(req_set)

    await runs.log_ai_run(
        session,
        task="m1.criteria.generate",
        provider=result.provider,
        model=result.model,
        prompt_version=1,
        input_payload=payload,
        output={"requirements": [c.model_dump() for c in criteria]},
        latency_ms=result.latency_ms,
        status="ok",
        actor_id=actor,
    )
    await audit.audit(
        session,
        actor_id=actor,
        action="m1.requirements.generate",
        entity_type="vacancy",
        entity_id=vacancy_id,
        after={"count": len(criteria)},
    )
    return RequirementSetOut.model_validate(req_set)


async def screen(
    session: AsyncSession, application_id: uuid.UUID, actor: uuid.UUID
) -> ScreeningResultOut:
    app_result = await session.execute(
        select(Application).where(Application.id == application_id)
    )
    app = app_result.scalar_one_or_none()
    if app is None:
        raise ProblemException(
            404, "about:blank", "Application not found", detail=str(application_id)
        )

    cand_result = await session.execute(
        select(Candidate).where(Candidate.id == app.candidate_id)
    )
    candidate = cand_result.scalar_one_or_none()
    if candidate is None:
        raise ProblemException(
            404, "about:blank", "Candidate not found", detail=str(app.candidate_id)
        )

    vacancy = await _load_vacancy(session, app.vacancy_id)

    req_result = await session.execute(
        select(VacancyRequirementSet)
        .where(
            VacancyRequirementSet.vacancy_id == app.vacancy_id,
            VacancyRequirementSet.is_active.is_(True),
        )
        .order_by(VacancyRequirementSet.created_at.desc())
        .limit(1)
    )
    req_set = req_result.scalar_one_or_none()
    criteria = req_set.requirements if req_set else []

    resume_text = await _latest_resume_text(session, app.candidate_id)

    payload = {
        "vacancy_title": vacancy.title,
        "candidate_name": f"{candidate.first_name} {candidate.last_name}",
        "resume_text": resume_text[:8000],
        "criteria_json": json.dumps(criteria, ensure_ascii=False),
    }
    result = await ai.complete("m1.screening.score", payload)
    parsed = parse_json_lenient(result.text)
    if not isinstance(parsed, dict):
        raise ProblemException(
            502, "about:blank", "AI returned invalid screening", detail=result.text[:200]
        )

    raw_per = parsed.get("per_criterion", [])
    per_criterion = [
        CriterionScore.model_validate(item) for item in raw_per if isinstance(item, dict)
    ]
    total_score = parsed.get("total_score")
    recommendation = parsed.get("recommendation")
    confidence = parsed.get("confidence")

    screening = M1ScreeningResult(
        application_id=application_id,
        vacancy_id=app.vacancy_id,
        candidate_id=app.candidate_id,
        requirement_set_id=req_set.id if req_set else None,
        total_score=float(total_score) if total_score is not None else None,
        recommendation=str(recommendation) if recommendation else None,
        confidence=float(confidence) if confidence is not None else None,
        per_criterion=[c.model_dump() for c in per_criterion],
        model=result.model,
        prompt_version=1,
        status="completed",
        is_stale=False,
    )
    session.add(screening)
    await session.flush()
    await session.refresh(screening)

    await runs.log_ai_run(
        session,
        task="m1.screening.score",
        provider=result.provider,
        model=result.model,
        prompt_version=1,
        input_payload=payload,
        output=parsed,
        latency_ms=result.latency_ms,
        status="ok",
        actor_id=actor,
    )
    await outbox.publish(
        session,
        event_type="screening.completed",
        aggregate_type="application",
        aggregate_id=application_id,
        payload={
            "total_score": screening.total_score,
            "recommendation": screening.recommendation,
            "confidence": screening.confidence,
        },
        actor=actor,
    )
    await audit.audit(
        session,
        actor_id=actor,
        action="m1.screening.run",
        entity_type="application",
        entity_id=application_id,
        after={
            "recommendation": screening.recommendation,
            "score": screening.total_score,
        },
    )
    return ScreeningResultOut.model_validate(screening)


async def get_result(
    session: AsyncSession, application_id: uuid.UUID
) -> ScreeningResultOut:
    result = await session.execute(
        select(M1ScreeningResult)
        .where(M1ScreeningResult.application_id == application_id)
        .order_by(M1ScreeningResult.created_at.desc())
        .limit(1)
    )
    screening = result.scalar_one_or_none()
    if screening is None:
        raise ProblemException(
            404,
            "about:blank",
            "Screening result not found",
            detail=str(application_id),
        )
    return ScreeningResultOut.model_validate(screening)
