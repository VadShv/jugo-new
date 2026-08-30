from __future__ import annotations

from httpx import AsyncClient

from jugo.modules.m4_searchmap.service import (
    PLATFORMS,
    build_query_passports,
    validate_passports,
)


async def test_m4_endpoints_registered(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    paths = resp.json()["paths"]
    assert "/api/v1/search-map/vacancies/{vacancy_id}:generate" in paths
    assert "/api/v1/search-map/vacancies/{vacancy_id}" in paths
    assert "/api/v1/search-map/maps/{map_id}" in paths


def test_build_query_passports() -> None:
    term_pool = {
        "atoms": ["python", "fastapi", "postgresql", "asyncio"],
        "exclusions": ["manager"],
    }
    passports = build_query_passports(term_pool, list(PLATFORMS), ["target-employer"])
    assert len(passports) == len(PLATFORMS)
    assert passports[0].platform == "hh.ru"
    assert "python" in passports[0].terms
    assert "target-employer" in passports[0].exclusions
    assert "NOT" in passports[0].query
    google = next(p for p in passports if p.platform == "google_xray")
    assert google.query.startswith("site:")


def test_build_query_passports_empty_atoms() -> None:
    passports = build_query_passports({"atoms": []}, list(PLATFORMS), [])
    assert passports == []


def test_validate_passports_clean() -> None:
    passports = build_query_passports({"atoms": ["a", "b", "c", "d"]}, ["hh.ru", "linkedin"], [])
    issues = validate_passports(passports)
    assert "high_intersection:hh.ru/linkedin" in issues


def test_validate_passports_no_intersection() -> None:
    from jugo.modules.m4_searchmap.schemas import QueryPassport

    passports = [
        QueryPassport(platform="hh.ru", query="q", terms=["a", "b"]),
        QueryPassport(platform="linkedin", query="q", terms=["c", "d"]),
    ]
    assert validate_passports(passports) == []


def test_validate_passports_empty() -> None:
    assert validate_passports([]) == ["no_passports"]
