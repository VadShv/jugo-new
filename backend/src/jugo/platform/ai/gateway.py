from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx
from pydantic import BaseModel

from jugo.core.config import get_settings


class AIResult(BaseModel):
    text: str
    output: dict[str, Any] | None = None
    model: str
    provider: str
    latency_ms: int = 0


class LLMProvider(ABC):
    name: str = ""

    @abstractmethod
    async def complete(
        self, task: str, payload: dict[str, Any], *, model: str | None = None
    ) -> AIResult:
        ...


class OpenAIProvider(LLMProvider):
    name = "openai"

    async def complete(
        self, task: str, payload: dict[str, Any], *, model: str | None = None
    ) -> AIResult:
        import openai

        settings = get_settings()
        client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        chosen = model or settings.openai_model
        resp = await client.chat.completions.create(
            model=chosen,
            messages=[{"role": "user", "content": str(payload)}],
        )
        content = resp.choices[0].message.content
        return AIResult(text=content or "", model=chosen, provider=self.name)


class YandexProvider(LLMProvider):
    name = "yandex"

    async def complete(
        self, task: str, payload: dict[str, Any], *, model: str | None = None
    ) -> AIResult:
        settings = get_settings()
        chosen = model or settings.yandex_model
        body = {
            "modelUri": f"gpt://{settings.yandex_folder_id}/{chosen}",
            "completionOptions": {"stream": False, "temperature": 0.2, "maxTokens": 2000},
            "messages": [{"role": "user", "text": str(payload)}],
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                settings.yandex_endpoint,
                json=body,
                headers={"Authorization": f"Api-Key {settings.yandex_api_key}"},
            )
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
        text = str(data["result"]["alternatives"][0]["message"]["text"])
        return AIResult(text=text, model=chosen, provider=self.name)


class LLMGateway:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider

    def _select(self) -> LLMProvider:
        if self._provider is not None:
            return self._provider
        settings = get_settings()
        if settings.ai_provider == "yandex":
            return YandexProvider()
        return OpenAIProvider()

    async def complete(
        self, task: str, payload: dict[str, Any], *, model: str | None = None
    ) -> AIResult:
        return await self._select().complete(task, payload, model=model)


ai = LLMGateway()

__all__ = ["AIResult", "LLMProvider", "OpenAIProvider", "YandexProvider", "LLMGateway", "ai"]
