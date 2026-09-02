from __future__ import annotations

from httpx import AsyncClient


async def test_workspace_endpoint_registered(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    paths = resp.json()["paths"]
    assert "/api/v1/workspace/vacancies/{vacancy_id}" in paths
