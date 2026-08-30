from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core import audit, outbox
from jugo.core.errors import ProblemException
from jugo.domains.applications.models import Application
from jugo.domains.candidates.models import Candidate
from jugo.domains.resumes.models import ResumeSource, ResumeVersion
from jugo.domains.vacancies.models import Vacancy
from jugo.modules.m2_risk.models import M2RiskReport
from jugo.modules.m2_risk.schemas import RiskReportOut, RiskSignal
from jugo.platform.ai import runs
from jugo.platform.ai.gateway import ai
from jugo.platform.ai.structured import parse_json_lenient

HIGH_RISK_CODES = {"document", "date_math", "cross_source"}
_SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}


def detect_date_overlap(periods: list[dict[str, Any]]) -> list[RiskSignal]:
    for i in range(len(periods)):
        for j in range(i + 1, len(periods)):
            a, b = periods[i], periods[j]
            a_end, b_start = a.get("end"), b.get("start")
            if a_end and b_start and a_end > b_start:
                return [
                    RiskSignal(
                        code="date_overlap",
                        severity="medium",
                        confidence=0.8,
                        evidence=(
                            f"Пересечение периодов: {a.get('company', '?')} "
                            f"и {b.get('company', '?')}"
                        ),
                        alternative_explanation="Возможно совмещение должностей",
                        verification_question="Было ли совмещение?",
                    )
                ]
    return []


def detect_job_hopping(tenures_months: list[int]) -> list[RiskSignal]:
    if len(tenures_months) < 3:
        return []
    avg = sum(tenures_months) / len(tenures_months)
    if avg < 6:
        return [
            RiskSignal(
                code="job_hopping",
                severity="medium",
                confidence=0.7,
                evidence=f"Средний срок {avg:.1f} мес на {len(tenures_months)} местах",
                alternative_explanation="Стажировки / проектная работа",
                verification_question="Причины частой смены работы?",
            )
        ]
    return []


def detect_salary_jump(salaries: list[int]) -> list[RiskSignal]:
    for i in range(1, len(salaries)):
        prev = salaries[i - 1]
        if prev > 0 and salaries[i] > prev * 2:
            return [
                RiskSignal(
                    code="salary_jump",
                    severity="low",
                    confidence=0.6,
                    evidence=f"Рост ЗП {prev} → {salaries[i]} (>2x)",
                    alternative_explanation="Смена специализации / региона / грейда",
                    verification_question="Чем обоснован рост зарплаты?",
                )
            ]
    return []


def compute_risk_level(signals: list[RiskSignal]) -> str:
    if any(s.code in HIGH_RISK_CODES for s in signals):
        return "high"
    if any(s.severity in ("medium", "high") for s in signals):
        return "medium"
    return "low"


def top_risks(signals: list[RiskSignal]) -> list[str]:
    ordered = sorted(signals, key=lambda s: _SEVERITY_RANK.get(s.severity, 3))
    result: list[str] = []
    for s in ordered:
        if s.code not in result:
            result.append(s.code)
        if len(result) >= 3:
            break
    return result


async def _load_vacancy(session: AsyncSession, vacancy_id: uuid.UUID) -> Vacancy:
    result = await session.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    vacancy = result.scalar_one_or_none()
    if vacancy is None:
        raise ProblemException(404, "about:blank", "Vacancy not found", detail=str(vacancy_id))
    return vacancy


async def _latest_resume_text(session: AsyncSession, candidate_id: uuid.UUID) -> str:
    result = await session.execute(
        select(ResumeVersion.parsed_text)
        .join(ResumeSource, ResumeSource.id == ResumeVersion.resume_source_id)
        .where(ResumeSource.candidate_id == candidate_id)
        .order_by(ResumeVersion.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none() or ""


async def analyze(
    session: AsyncSession, application_id: uuid.UUID, actor: uuid.UUID
) -> RiskReportOut:
    app_result = await session.execute(select(Application).where(Application.id == application_id))
    app = app_result.scalar_one_or_none()
    if app is None:
        raise ProblemException(
            404, "about:blank", "Application not found", detail=str(application_id)
        )

    cand_result = await session.execute(select(Candidate).where(Candidate.id == app.candidate_id))
    candidate = cand_result.scalar_one_or_none()
    if candidate is None:
        raise ProblemException(
            404, "about:blank", "Candidate not found", detail=str(app.candidate_id)
        )

    vacancy = await _load_vacancy(session, app.vacancy_id)
    resume_text = await _latest_resume_text(session, app.candidate_id)

    payload = {
        "vacancy_title": vacancy.title,
        "candidate_name": f"{candidate.first_name} {candidate.last_name}",
        "resume_text": resume_text[:8000],
    }
    result = await ai.complete("m2.risk.analyze", payload)
    parsed = parse_json_lenient(result.text)
    if not isinstance(parsed, dict):
        raise ProblemException(
            502, "about:blank", "AI returned invalid risk", detail=result.text[:200]
        )

    raw_signals = parsed.get("signals", [])
    signals = [RiskSignal.model_validate(s) for s in raw_signals if isinstance(s, dict)]
    risk_level = compute_risk_level(signals)
    top = top_risks(signals)
    summary = parsed.get("summary")

    report = M2RiskReport(
        application_id=application_id,
        candidate_id=app.candidate_id,
        vacancy_id=app.vacancy_id,
        risk_level=risk_level,
        signals=[s.model_dump() for s in signals],
        top_risks=top,
        summary=str(summary) if summary else None,
        model=result.model,
        prompt_version=1,
        status="completed",
    )
    session.add(report)
    await session.flush()
    await session.refresh(report)

    await session.execute(
        update(Application).where(Application.id == application_id).values(risk_level=risk_level)
    )

    await runs.log_ai_run(
        session,
        task="m2.risk.analyze",
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
        event_type="risk.analysis.completed",
        aggregate_type="application",
        aggregate_id=application_id,
        payload={"risk_level": risk_level, "top_risks": top},
        actor=actor,
    )
    await audit.audit(
        session,
        actor_id=actor,
        action="m2.risk.run",
        entity_type="application",
        entity_id=application_id,
        after={"risk_level": risk_level},
    )
    return RiskReportOut.model_validate(report)


async def get_report(session: AsyncSession, application_id: uuid.UUID) -> RiskReportOut:
    result = await session.execute(
        select(M2RiskReport)
        .where(M2RiskReport.application_id == application_id)
        .order_by(M2RiskReport.created_at.desc())
        .limit(1)
    )
    report = result.scalar_one_or_none()
    if report is None:
        raise ProblemException(
            404, "about:blank", "Risk report not found", detail=str(application_id)
        )
    return RiskReportOut.model_validate(report)
