from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape


class PromptRegistry:
    def __init__(self, templates_dir: Path | None = None) -> None:
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "prompts"
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape([]),
            enable_async=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, task: str, version: str = "default", **variables: Any) -> str:
        candidates = [f"{task}/{version}.j2", f"{task}.j2"]
        for name in candidates:
            try:
                template = self.env.get_template(name)
            except TemplateNotFound:
                continue
            return template.render(**variables)
        return self._fallback(task, **variables)

    def _fallback(self, task: str, **variables: Any) -> str:
        return f"Task: {task}\nPayload: {json.dumps(variables, default=str)}"
