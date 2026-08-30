from __future__ import annotations

from httpx import AsyncClient

from jugo.platform.ai.structured import parse_json_lenient


async def test_m1_endpoints_registered(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    paths = resp.json()["paths"]
    assert "/api/v1/screening/vacancies/{vacancy_id}/requirements:generate" in paths
    assert "/api/v1/screening/applications/{application_id}:run" in paths
    assert "/api/v1/screening/applications/{application_id}" in paths


def test_parse_json_lenient_fenced() -> None:
    text = '```json\n{"total_score": 0.8, "recommendation": "recommend"}\n```'
    data = parse_json_lenient(text)
    assert data == {"total_score": 0.8, "recommendation": "recommend"}


def test_parse_json_lenient_bare() -> None:
    text = 'окружающий текст {"a": 1, "b": [2, 3]} хвост'
    data = parse_json_lenient(text)
    assert data == {"a": 1, "b": [2, 3]}


def test_parse_json_lenient_invalid() -> None:
    assert parse_json_lenient("not json at all") is None
