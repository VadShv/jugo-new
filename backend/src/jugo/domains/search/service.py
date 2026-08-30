from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from jugo.core.db import decode_cursor, encode_cursor

DEFAULT_LIMIT = 25
MAX_LIMIT = 100
SIMILARITY_THRESHOLD = 0.1

_CANDIDATE_FILTERS = {"grade", "location", "is_blacklisted"}
_VACANCY_FILTERS = {"status"}
_APPLICATION_FILTERS = {"status", "origin", "risk_level"}


class SearchRequest(BaseModel):
    q: str = Field(..., min_length=1, max_length=512)
    limit: int = Field(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT)
    cursor: str | None = None
    filters: dict[str, str] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    items: list[dict[str, Any]]
    next_cursor: str | None = None
    has_more: bool = False


def _resolve_offset(cursor: str | None) -> int:
    if cursor is None:
        return 0
    key = decode_cursor(cursor)
    return int(key.get("offset", 0))


def _next_cursor(offset: int, has_more: bool) -> str | None:
    if not has_more:
        return None
    return encode_cursor({"offset": offset})


def _serialize(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in row.items():
        if value is None or isinstance(value, (int, float, bool, str)):
            out[key] = value
        elif hasattr(value, "isoformat"):
            out[key] = value.isoformat()
        else:
            out[key] = str(value)
    return out


def _candidate_filter_clause(filters: dict[str, str]) -> tuple[str, dict[str, Any]]:
    clauses: list[str] = []
    params: dict[str, Any] = {}
    for key, value in filters.items():
        if key not in _CANDIDATE_FILTERS:
            continue
        clauses.append(f"{key} = :f_{key}")
        params[f"f_{key}"] = value
    return (" AND ".join(clauses), params) if clauses else ("", params)


async def search_candidates(
    session: AsyncSession, request: SearchRequest
) -> SearchResponse:
    offset = _resolve_offset(request.cursor)
    extra, fparams = _candidate_filter_clause(request.filters)
    where = (
        "(search_vector @@ websearch_to_tsquery('russian', :q) "
        "OR similarity(coalesce(last_name,'')||' '||coalesce(first_name,'') "
        "||' '||coalesce(headline,''), :q) > :thr)"
    )
    if extra:
        where += " AND " + extra
    sql = text(
        f"""
        SELECT id, tenant_id, first_name, last_name, headline, current_company,
               grade, location, is_blacklisted, created_at, updated_at,
               ts_rank_cd(search_vector, websearch_to_tsquery('russian', :q)) AS rank
        FROM candidates
        WHERE {where}
        ORDER BY rank DESC, updated_at DESC, id DESC
        LIMIT :limit OFFSET :offset
        """
    )
    params: dict[str, Any] = {
        "q": request.q,
        "thr": SIMILARITY_THRESHOLD,
        "limit": request.limit + 1,
        "offset": offset,
    }
    params.update(fparams)
    result = await session.execute(sql, params)
    rows = [dict(r) for r in result.mappings()]
    has_more = len(rows) > request.limit
    items = [_serialize(r) for r in rows[: request.limit]]
    return SearchResponse(
        items=items,
        next_cursor=_next_cursor(offset + request.limit, has_more),
        has_more=has_more,
    )


async def search_vacancies(
    session: AsyncSession, request: SearchRequest
) -> SearchResponse:
    offset = _resolve_offset(request.cursor)
    extra_clauses: list[str] = []
    vparams: dict[str, Any] = {}
    for key, value in request.filters.items():
        if key not in _VACANCY_FILTERS:
            continue
        extra_clauses.append(f"{key} = :f_{key}")
        vparams[f"f_{key}"] = value
    where = (
        "(search_vector @@ websearch_to_tsquery('russian', :q) "
        "OR similarity(coalesce(title,'')||' '||coalesce(description,''), :q) > :thr)"
    )
    if extra_clauses:
        where += " AND " + " AND ".join(extra_clauses)
    sql = text(
        f"""
        SELECT id, tenant_id, title, description, status, headcount,
               recruiter_id, hiring_manager_id, created_at, updated_at,
               ts_rank_cd(search_vector, websearch_to_tsquery('russian', :q)) AS rank
        FROM vacancies
        WHERE {where}
        ORDER BY rank DESC, updated_at DESC, id DESC
        LIMIT :limit OFFSET :offset
        """
    )
    params = {
        "q": request.q,
        "thr": SIMILARITY_THRESHOLD,
        "limit": request.limit + 1,
        "offset": offset,
    }
    params.update(vparams)
    result = await session.execute(sql, params)
    rows = [dict(r) for r in result.mappings()]
    has_more = len(rows) > request.limit
    items = [_serialize(r) for r in rows[: request.limit]]
    return SearchResponse(
        items=items,
        next_cursor=_next_cursor(offset + request.limit, has_more),
        has_more=has_more,
    )


async def search_applications(
    session: AsyncSession, request: SearchRequest
) -> SearchResponse:
    offset = _resolve_offset(request.cursor)
    extra_clauses: list[str] = []
    aparams: dict[str, Any] = {}
    for key, value in request.filters.items():
        if key not in _APPLICATION_FILTERS:
            continue
        extra_clauses.append(f"a.{key} = :f_{key}")
        aparams[f"f_{key}"] = value
    where = (
        "(c.search_vector @@ websearch_to_tsquery('russian', :q) "
        "OR similarity(coalesce(c.last_name,'')||' '||coalesce(c.first_name,''), :q) > :thr)"
    )
    if extra_clauses:
        where += " AND " + " AND ".join(extra_clauses)
    sql = text(
        f"""
        SELECT a.id, a.tenant_id, a.candidate_id, a.vacancy_id, a.current_stage_id,
               a.origin, a.status, a.screening_score, a.risk_level,
               a.created_at, a.updated_at,
               ts_rank_cd(c.search_vector, websearch_to_tsquery('russian', :q)) AS rank
        FROM applications a
        JOIN candidates c ON c.id = a.candidate_id
        WHERE {where}
        ORDER BY rank DESC, a.updated_at DESC, a.id DESC
        LIMIT :limit OFFSET :offset
        """
    )
    params = {
        "q": request.q,
        "thr": SIMILARITY_THRESHOLD,
        "limit": request.limit + 1,
        "offset": offset,
    }
    params.update(aparams)
    result = await session.execute(sql, params)
    rows = [dict(r) for r in result.mappings()]
    has_more = len(rows) > request.limit
    items = [_serialize(r) for r in rows[: request.limit]]
    return SearchResponse(
        items=items,
        next_cursor=_next_cursor(offset + request.limit, has_more),
        has_more=has_more,
    )


async def search(
    session: AsyncSession, entity: str, request: SearchRequest
) -> SearchResponse:
    dispatch = {
        "candidates": search_candidates,
        "vacancies": search_vacancies,
        "applications": search_applications,
    }
    handler = dispatch.get(entity)
    if handler is None:
        from jugo.core.errors import ProblemException

        raise ProblemException(
            status=400,
            type_="about:blank",
            title="Unknown search entity",
            detail=entity,
        )
    return await handler(session, request)
