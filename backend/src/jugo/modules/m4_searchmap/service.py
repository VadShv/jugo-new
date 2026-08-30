from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core import audit, outbox
from jugo.core.errors import ProblemException
from jugo.domains.vacancies.models import Vacancy
from jugo.modules.m4_searchmap.models import M4SearchMap
from jugo.modules.m4_searchmap.schemas import QueryPassport, SearchMapOut
from jugo.platform.ai import runs
from jugo.platform.ai.gateway import ai
from jugo.platform.ai.structured import parse_json_lenient

PLATFORMS: tuple[str, ...] = ("hh.ru", "google_xray", "linkedin", "github", "habr")
TERM_BUDGET = 8
EXCLUSION_BUDGET = 5
MAX_INTERSECTION = 0.8


def build_query_passports(
    term_pool: dict[str, Any],
    platforms: list[str],
    anti_map: list[str],
) -> list[QueryPassport]:
    atoms = [str(t) for t in (term_pool.get("atoms") or []) if t]
    raw_exclusions = [str(e) for e in (term_pool.get("exclusions") or []) if e]
    exclusions = list(dict.fromkeys(raw_exclusions + anti_map))[:EXCLUSION_BUDGET]
    passports: list[QueryPassport] = []
    for platform in platforms:
        terms = atoms[:TERM_BUDGET]
        if not terms:
            continue
        body = " OR ".join(terms)
        query = f"({body})"
        if exclusions:
            query += " NOT (" + " OR ".join(exclusions) + ")"
        if platform == "google_xray":
            query = f"site:hh.ru OR site:linkedin.com {query}"
        passports.append(
            QueryPassport(
                platform=platform,
                query=query,
                terms=terms,
                exclusions=exclusions,
            )
        )
    return passports


def validate_passports(passports: list[QueryPassport]) -> list[str]:
    issues: list[str] = []
    if not passports:
        issues.append("no_passports")
        return issues
    term_sets = [set(p.terms) for p in passports]
    for i in range(len(term_sets)):
        for j in range(i + 1, len(term_sets)):
            union = term_sets[i] | term_sets[j]
            if not union:
                continue
            intersection = term_sets[i] & term_sets[j]
            if len(intersection) / len(union) > MAX_INTERSECTION:
                issues.append(f"high_intersection:{passports[i].platform}/{passports[j].platform}")
    if any(len(p.terms) == 0 for p in passports):
        issues.append("empty_terms")
    return issues


async def _load_vacancy(session: AsyncSession, vacancy_id: uuid.UUID) -> Vacancy:
    result = await session.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    vacancy = result.scalar_one_or_none()
    if vacancy is None:
        raise ProblemException(404, "about:blank", "Vacancy not found", detail=str(vacancy_id))
    return vacancy


async def generate(session: AsyncSession, vacancy_id: uuid.UUID, actor: uuid.UUID) -> SearchMapOut:
    vacancy = await _load_vacancy(session, vacancy_id)
    base = {
        "vacancy_title": vacancy.title,
        "vacancy_description": vacancy.description or "",
    }

    r1 = await ai.complete("m4.role.ontology", base)
    parsed_ontology = parse_json_lenient(r1.text)
    ontology: dict[str, Any] = parsed_ontology if isinstance(parsed_ontology, dict) else {}
    await runs.log_ai_run(
        session,
        task="m4.role.ontology",
        provider=r1.provider,
        model=r1.model,
        prompt_version=1,
        input_payload=base,
        output=ontology,
        latency_ms=r1.latency_ms,
        status="ok",
        actor_id=actor,
    )

    r2 = await ai.complete("m4.donors", {**base, "ontology": ontology})
    parsed_donors = parse_json_lenient(r2.text)
    donors_data: dict[str, Any] = parsed_donors if isinstance(parsed_donors, dict) else {}
    donors = donors_data.get("donors") or []
    hypotheses = donors_data.get("hypotheses") or []
    anti_map_raw = donors_data.get("anti_map") or []
    anti_map = [str(x) for x in anti_map_raw if x]
    await runs.log_ai_run(
        session,
        task="m4.donors",
        provider=r2.provider,
        model=r2.model,
        prompt_version=1,
        input_payload={**base, "ontology": ontology},
        output=donors_data,
        latency_ms=r2.latency_ms,
        status="ok",
        actor_id=actor,
    )

    r3 = await ai.complete("m4.terms", {"ontology": ontology, "donors": donors})
    parsed_terms = parse_json_lenient(r3.text)
    term_pool: dict[str, Any] = parsed_terms if isinstance(parsed_terms, dict) else {}
    await runs.log_ai_run(
        session,
        task="m4.terms",
        provider=r3.provider,
        model=r3.model,
        prompt_version=1,
        input_payload={"ontology": ontology},
        output=term_pool,
        latency_ms=r3.latency_ms,
        status="ok",
        actor_id=actor,
    )

    passports = build_query_passports(term_pool, list(PLATFORMS), anti_map)
    validation_issues = validate_passports(passports)

    r4 = await ai.complete("m4.justifications", {"passports": [p.model_dump() for p in passports]})
    parsed_just = parse_json_lenient(r4.text)
    justifications: dict[str, Any] = parsed_just if isinstance(parsed_just, dict) else {}
    await runs.log_ai_run(
        session,
        task="m4.justifications",
        provider=r4.provider,
        model=r4.model,
        prompt_version=1,
        input_payload={"passports": [p.model_dump() for p in passports]},
        output=justifications,
        latency_ms=r4.latency_ms,
        status="ok",
        actor_id=actor,
    )

    latest_result = await session.execute(
        select(M4SearchMap.version_no)
        .where(M4SearchMap.vacancy_id == vacancy_id)
        .order_by(M4SearchMap.version_no.desc())
        .limit(1)
    )
    latest = latest_result.scalar_one_or_none()
    next_version = (latest + 1) if latest else 1

    smap = M4SearchMap(
        vacancy_id=vacancy_id,
        version_no=next_version,
        status="draft",
        role_ontology=ontology,
        donors=donors,
        hypotheses=hypotheses,
        anti_map=anti_map,
        term_pool=term_pool,
        query_passports=[p.model_dump() for p in passports],
        justifications=justifications,
        model=r1.model,
        prompt_version=1,
    )
    session.add(smap)
    await session.flush()
    await session.refresh(smap)

    await outbox.publish(
        session,
        event_type="searchmap.generated",
        aggregate_type="vacancy",
        aggregate_id=vacancy_id,
        payload={
            "map_id": str(smap.id),
            "version_no": next_version,
            "validation_issues": validation_issues,
        },
        actor=actor,
    )
    await audit.audit(
        session,
        actor_id=actor,
        action="m4.searchmap.generate",
        entity_type="vacancy",
        entity_id=vacancy_id,
        after={"map_id": str(smap.id), "passports": len(passports)},
    )
    return SearchMapOut.model_validate(smap)


async def get_latest(session: AsyncSession, vacancy_id: uuid.UUID) -> SearchMapOut:
    result = await session.execute(
        select(M4SearchMap)
        .where(M4SearchMap.vacancy_id == vacancy_id)
        .order_by(M4SearchMap.version_no.desc())
        .limit(1)
    )
    smap = result.scalar_one_or_none()
    if smap is None:
        raise ProblemException(404, "about:blank", "Search map not found", detail=str(vacancy_id))
    return SearchMapOut.model_validate(smap)


async def get(session: AsyncSession, map_id: uuid.UUID) -> SearchMapOut:
    result = await session.execute(select(M4SearchMap).where(M4SearchMap.id == map_id))
    smap = result.scalar_one_or_none()
    if smap is None:
        raise ProblemException(404, "about:blank", "Search map not found", detail=str(map_id))
    return SearchMapOut.model_validate(smap)
