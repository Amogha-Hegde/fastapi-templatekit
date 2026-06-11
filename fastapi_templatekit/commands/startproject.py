from __future__ import annotations

import argparse
from pathlib import Path

from fastapi_templatekit.commands.rendering import render_template
from fastapi_templatekit.commands.validation import normalize_package_name, validate_package_name


PROJECT_TEMPLATES = (
    ("project/pyproject.toml.tpl", "pyproject.toml"),
    ("project/gitignore.tpl", ".gitignore"),
    ("project/fastapi_templatekit.toml.tpl", "fastapi_templatekit.toml"),
    ("project/env.example.tpl", ".env.example"),
    ("project/README.md.tpl", "README.md"),
    ("project/package/__init__.py.tpl", "{package_name}/__init__.py"),
    ("project/package/cli.py.tpl", "{package_name}/cli.py"),
    ("project/package/main.py.tpl", "{package_name}/main.py"),
    ("project/package/config.py.tpl", "{package_name}/config.py"),
    ("project/package/router.py.tpl", "{package_name}/router.py"),
)


def add_startproject_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "startproject",
        help="Create a new FastAPI project.",
    )
    parser.add_argument("name", help="Project name.")
    parser.add_argument(
        "directory",
        nargs="?",
        help="Optional destination directory. Use '.' to create files in the current directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing project files without prompting.",
    )
    parser.set_defaults(handler=handle_startproject)


def handle_startproject(args: argparse.Namespace) -> None:
    project_name = args.name.strip()
    package_name = validate_package_name(
        normalize_package_name(project_name),
        "Project name",
    )
    target_dir = Path(args.directory or project_name).resolve()

    if target_dir.exists() and not target_dir.is_dir():
        raise SystemExit(f"Error: target path exists and is not a directory: {target_dir}")

    context = {
        "project_name": project_name,
        "package_name": package_name,
    }

    destinations = [
        target_dir / destination_pattern.format(**context)
        for _, destination_pattern in PROJECT_TEMPLATES
    ]
    existing_paths = [destination for destination in destinations if destination.exists()]

    if existing_paths and not args.force:
        conflicts = "\n".join(f"  {path}" for path in existing_paths)
        print(f"Project files already exist:\n{conflicts}")
        answer = input("Overwrite these files? [y/N]: ").strip().lower()
        if answer not in {"y", "yes"}:
            raise SystemExit("Aborted.")

    for template_path, destination_pattern in PROJECT_TEMPLATES:
        destination = target_dir / destination_pattern.format(**context)
        render_template(template_path, destination, context)

    print(f"Created FastAPI project '{project_name}' at {target_dir}")
    print(f"Next steps:")
    if target_dir != Path.cwd().resolve():
        print(f"  cd {target_dir}")
    print(f"  uv sync")
    print(f"  uv run uvicorn {package_name}.main:app --reload")
    print(f"  uv run {package_name} urls")
