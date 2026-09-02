from __future__ import annotations

from httpx import AsyncClient


async def test_comments_endpoints_registered(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    paths = resp.json()["paths"]
    assert "/api/v1/applications/{application_id}/comments" in paths
    assert "/api/v1/comments/{comment_id}" in paths
