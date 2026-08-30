from __future__ import annotations

from httpx import AsyncClient


async def test_live(client: AsyncClient) -> None:
    resp = await client.get("/live")
    assert resp.status_code == 200
    assert resp.json()["status"] == "alive"


async def test_openapi(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    paths = resp.json()["paths"]
    assert "/api/v1/candidates" in paths
    assert "/api/v1/vacancies" in paths
    assert "/api/v1/applications" in paths
