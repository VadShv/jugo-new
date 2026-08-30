from __future__ import annotations

from httpx import AsyncClient

from jugo.modules.m2_risk.schemas import RiskSignal
from jugo.modules.m2_risk.service import (
    compute_risk_level,
    detect_date_overlap,
    detect_job_hopping,
    detect_salary_jump,
    top_risks,
)


async def test_m2_endpoints_registered(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    paths = resp.json()["paths"]
    assert "/api/v1/risk/applications/{application_id}:run" in paths
    assert "/api/v1/risk/applications/{application_id}" in paths


def _sig(code: str, severity: str = "medium") -> RiskSignal:
    return RiskSignal(code=code, severity=severity, confidence=0.7)


def test_compute_risk_level() -> None:
    assert compute_risk_level([_sig("date_math")]) == "high"
    assert compute_risk_level([_sig("document")]) == "high"
    assert compute_risk_level([_sig("date_overlap", "medium")]) == "medium"
    assert compute_risk_level([_sig("salary_jump", "low")]) == "low"
    assert compute_risk_level([]) == "low"


def test_detect_date_overlap() -> None:
    overlap = [
        {"company": "A", "start": "2018-01", "end": "2020-06"},
        {"company": "B", "start": "2020-01", "end": "2022-01"},
    ]
    sigs = detect_date_overlap(overlap)
    assert len(sigs) == 1
    assert sigs[0].code == "date_overlap"
    clean = [
        {"company": "A", "start": "2018-01", "end": "2020-01"},
        {"company": "B", "start": "2020-02", "end": "2022-01"},
    ]
    assert detect_date_overlap(clean) == []


def test_detect_job_hopping() -> None:
    assert detect_job_hopping([3, 4, 5]) != []
    assert detect_job_hopping([12, 14, 16]) == []
    assert detect_job_hopping([5, 5]) == []


def test_detect_salary_jump() -> None:
    assert detect_salary_jump([100, 250]) != []
    assert detect_salary_jump([100, 150]) == []


def test_top_risks() -> None:
    sigs = [_sig("a", "low"), _sig("b", "high"), _sig("c", "medium")]
    assert top_risks(sigs) == ["b", "c", "a"]
