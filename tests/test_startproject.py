from __future__ import annotations

import argparse

from fastapi_template.commands import startproject


def test_startproject_generates_gitignore_for_python_build_artifacts(tmp_path) -> None:
    target_dir = tmp_path / "demo"

    startproject.handle_startproject(
        argparse.Namespace(
            name="demo",
            directory=str(target_dir),
            force=False,
        )
    )

    gitignore = (target_dir / ".gitignore").read_text(encoding="utf-8")

    assert "*.egg-info/" in gitignore
    assert ".venv/" in gitignore
    assert "__pycache__/" in gitignore
