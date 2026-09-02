from __future__ import annotations

from httpx import AsyncClient


async def test_tasks_endpoints_registered(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    paths = resp.json()["paths"]
    assert "/api/v1/applications/{application_id}/tasks" in paths
    assert "/api/v1/tasks" in paths
    assert "/api/v1/tasks/{task_id}" in paths
