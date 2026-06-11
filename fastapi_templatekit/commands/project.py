from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any


def load_project_config(project_root: Path) -> dict[str, Any]:
    marker_path = project_root / "fastapi_templatekit.toml"

    if not marker_path.exists():
        raise SystemExit(
            "Error: command must be run inside a fastapi-templatekit project.\n"
            "Run: fastapi-templatekit startproject <project_name>"
        )

    marker = tomllib.loads(marker_path.read_text(encoding="utf-8"))
    project = marker.get("project", {})
    if not isinstance(project, dict):
        raise SystemExit(f"Error: invalid project config: {marker_path}")

    return project
