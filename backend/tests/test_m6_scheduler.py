from __future__ import annotations

from datetime import date

from httpx import AsyncClient

from jugo.modules.m6_scheduler.schemas import Window
from jugo.modules.m6_scheduler.service import _intersect_windows, suggest_slots


async def test_m6_endpoints_registered(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    paths = resp.json()["paths"]
    assert "/api/v1/interviews/slots:suggest" in paths
    assert "/api/v1/interviews" in paths
    assert "/api/v1/interviews/{interview_id}:reschedule" in paths
    assert "/api/v1/interviews/{interview_id}:cancel" in paths
    assert "/api/v1/interviews/{interview_id}:feedback" in paths


def test_suggest_slots_basic() -> None:
    d = date(2026, 8, 31)
    windows = [Window(day_of_week=d.weekday(), start="10:00", end="13:00")]
    slots = suggest_slots(windows, d, d, duration_min=60, buffer_min=15, limit_per_day=3)
    assert len(slots) == 2
    assert slots[0].hour == 10 and slots[0].minute == 0
    assert slots[1].hour == 11 and slots[1].minute == 15


def test_suggest_slots_respects_working_hours() -> None:
    d = date(2026, 8, 31)
    windows = [Window(day_of_week=d.weekday(), start="07:00", end="20:00")]
    slots = suggest_slots(windows, d, d, duration_min=60, buffer_min=15, limit_per_day=10)
    assert slots[0].hour == 9
    assert slots[-1].hour < 18


def test_suggest_slots_no_window_for_dow() -> None:
    d = date(2026, 8, 31)
    windows = [Window(day_of_week=(d.weekday() + 1) % 7, start="10:00", end="12:00")]
    assert suggest_slots(windows, d, d) == []


def test_intersect_windows() -> None:
    a = [Window(day_of_week=0, start="09:00", end="13:00")]
    b = [Window(day_of_week=0, start="11:00", end="18:00")]
    common = _intersect_windows([a, b])
    assert len(common) == 1
    assert common[0].start == "11:00"
    assert common[0].end == "13:00"


def test_intersect_windows_no_overlap() -> None:
    a = [Window(day_of_week=0, start="09:00", end="10:00")]
    b = [Window(day_of_week=0, start="11:00", end="12:00")]
    assert _intersect_windows([a, b]) == []
