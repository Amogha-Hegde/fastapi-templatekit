from __future__ import annotations

from importlib import resources
from pathlib import Path
from string import Template


TEMPLATE_ROOT = "fastapi_template.templates"


def render_template(template_path: str, destination: Path, context: dict[str, str]) -> None:
    template = resources.files(TEMPLATE_ROOT).joinpath(template_path)
    content = Template(template.read_text(encoding="utf-8")).safe_substitute(context)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
