from __future__ import annotations

from httpx import AsyncClient

from jugo.modules.m3_questions.schemas import QuestionCard
from jugo.modules.m3_questions.service import (
    check_open_ended,
    check_personalized,
    check_stop_words,
    validate_question,
)


async def test_m3_endpoints_registered(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    paths = resp.json()["paths"]
    assert "/api/v1/questions/vacancies/{vacancy_id}:generate" in paths
    assert "/api/v1/questions/sets/{set_id}:approve" in paths
    assert "/api/v1/questions/vacancies/{vacancy_id}" in paths
    assert "/api/v1/questions/sets/{set_id}" in paths


def test_check_stop_words() -> None:
    assert check_stop_words("Какой у вас возраст?") != []
    assert check_stop_words("Расскажите о проекте") == []


def test_check_open_ended() -> None:
    assert check_open_ended("Расскажите, как вы решали конфликт")
    assert not check_open_ended("Вы работали с Python?")


def test_check_personalized() -> None:
    assert check_personalized("Иван, приведите пример", "Иван Иванов")
    assert check_personalized("Приведите пример ситуации", None)
    assert not check_personalized("Опыт работы с Python", None)


def test_validate_question_flags_issues() -> None:
    bad = QuestionCard(question="Какой у вас возраст и пол?")
    validated = validate_question(bad, None)
    assert not validated.valid
    assert any("stop_words" in i for i in validated.validation_issues)

    good = QuestionCard(question="Расскажите, как вы решали конфликт в команде")
    validated_good = validate_question(good, None)
    assert validated_good.valid
    assert validated_good.validation_issues == []
