from __future__ import annotations

from httpx import AsyncClient


async def test_m5_endpoints_registered(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    paths = resp.json()["paths"]
    assert "/api/v1/analytics/funnel/{vacancy_id}" in paths
    assert "/api/v1/analytics/sources" in paths
    assert "/api/v1/analytics/ai" in paths
    assert "/api/v1/analytics/recruiters" in paths
