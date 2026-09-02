from __future__ import annotations

from httpx import AsyncClient


async def test_reject_endpoints_registered(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    paths = resp.json()["paths"]
    assert "/api/v1/applications/{application_id}/reject" in paths
    assert "/api/v1/applications/{application_id}/restore" in paths
    assert "/api/v1/applications/dictionaries/reject-reasons" in paths
