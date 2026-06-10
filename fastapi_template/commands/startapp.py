from __future__ import annotations

import argparse
import tomllib
from pathlib import Path

from fastapi_template.commands.project import load_project_config
from fastapi_template.commands.rendering import render_template
from fastapi_template.commands.validation import normalize_package_name, validate_package_name


BASE_APP_TEMPLATES = (
    ("app/__init__.py.tpl", "{app_name}/__init__.py"),
    ("app/router.py.tpl", "{app_name}/router.py"),
    ("app/endpoints/__init__.py.tpl", "{app_name}/endpoints/__init__.py"),
    ("app/endpoints/api.py.tpl", "{app_name}/endpoints/api.py"),
    ("app/schemas/__init__.py.tpl", "{app_name}/schemas/__init__.py"),
    ("app/schemas/validator.py.tpl", "{app_name}/schemas/validator.py"),
    ("app/service/__init__.py.tpl", "{app_name}/service/__init__.py"),
    ("app/service/app_service.py.tpl", "{app_name}/service/{app_name}_service.py"),
)

DATABASE_APP_TEMPLATES = (
    ("app/models/__init__.py.tpl", "{app_name}/models/__init__.py"),
)

WEBSOCKET_APP_TEMPLATES = (
    ("app/websocket/__init__.py.tpl", "{app_name}/websocket/__init__.py"),
    ("app/websocket/router.py.tpl", "{app_name}/websocket/router.py"),
)

WEBSOCKET_DEPENDENCY = "fastapi-websockets"


def add_startapp_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "startapp",
        help="Create a FastAPI app inside an existing generated project.",
    )
    parser.add_argument("name", help="App name.")
    parser.add_argument(
        "--with-websockets",
        action="store_true",
        help="Add a websocket folder with a sample websocket route.",
    )
    parser.add_argument(
        "--with-database",
        action="store_true",
        help="Add a models folder for database tables.",
    )
    parser.set_defaults(handler=handle_startapp)


def handle_startapp(args: argparse.Namespace) -> None:
    project_root = Path.cwd()
    project = load_project_config(project_root)
    apps_dir = project_root / project.get("apps_dir", ".")

    app_name = validate_package_name(
        normalize_package_name(args.name),
        "App name",
    )
    app_dir = apps_dir / app_name

    if app_dir.exists():
        raise SystemExit(f"Error: app already exists: {app_dir}")

    include_websockets = args.with_websockets or ask_yes_no("Do you want to include websockets?")
    include_database = args.with_database or ask_yes_no("Do you want to include database/tables?")

    context = {
        "app_name": app_name,
        "app_class_name": "".join(part.capitalize() for part in app_name.split("_")),
        "route_prefix": app_name.replace("_", "-"),
    }

    templates = list(BASE_APP_TEMPLATES)
    if include_database:
        templates.extend(DATABASE_APP_TEMPLATES)
    if include_websockets:
        templates.extend(WEBSOCKET_APP_TEMPLATES)

    for template_path, destination_pattern in templates:
        destination = apps_dir / destination_pattern.format(**context)
        render_template(template_path, destination, context)

    if include_websockets:
        ensure_project_dependency(project_root, WEBSOCKET_DEPENDENCY)

    print(f"Created FastAPI app '{app_name}' at {app_dir}")
    print("Register the router in your project API router:")
    print(f"  from {app_name}.router import router as {app_name}_router")
    print(f"  api_router.include_router({app_name}_router, prefix=\"/{context['route_prefix']}\", tags=[\"{app_name}\"])")
    if include_websockets:
        print("Register the websocket router in your project API router:")
        print(f"  from {app_name}.websocket.router import router as {app_name}_websocket_router")
        print(f"  api_router.include_router({app_name}_websocket_router, prefix=\"/{context['route_prefix']}\")")


def ask_yes_no(question: str) -> bool:
    try:
        answer = input(f"{question} [y/N]: ").strip().lower()
    except EOFError:
        return False
    return answer in {"y", "yes"}


def ensure_project_dependency(project_root: Path, dependency: str) -> None:
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        raise SystemExit(f"Error: missing project config: {pyproject_path}")

    content = pyproject_path.read_text(encoding="utf-8")
    parsed = tomllib.loads(content)
    dependencies = parsed.get("project", {}).get("dependencies", [])
    if not isinstance(dependencies, list):
        dependencies = []

    dependency_name = normalize_dependency_name(dependency)
    if any(normalize_dependency_name(item) == dependency_name for item in dependencies):
        return

    lines = content.splitlines(keepends=True)
    dependencies_start = next(
        (index for index, line in enumerate(lines) if line.strip() == "dependencies = ["),
        None,
    )

    if dependencies_start is None:
        project_start = next(
            (index for index, line in enumerate(lines) if line.strip() == "[project]"),
            None,
        )
        if project_start is None:
            raise SystemExit(f"Error: invalid project config: {pyproject_path}")
        lines[project_start + 1 : project_start + 1] = [
            "dependencies = [\n",
            f'    "{dependency}",\n',
            "]\n",
        ]
        pyproject_path.write_text("".join(lines), encoding="utf-8")
        return

    dependencies_end = next(
        (
            index
            for index in range(dependencies_start + 1, len(lines))
            if lines[index].strip() == "]"
        ),
        None,
    )
    if dependencies_end is None:  # pragma: no cover
        raise SystemExit(f"Error: invalid dependencies array: {pyproject_path}")

    lines.insert(dependencies_end, f'    "{dependency}",\n')
    pyproject_path.write_text("".join(lines), encoding="utf-8")


def normalize_dependency_name(dependency: object) -> str:
    if not isinstance(dependency, str):
        return ""
    name = dependency
    for separator in ("[", "<", ">", "=", "~", "!", ";"):
        name = name.split(separator, 1)[0]
    return name.strip().lower().replace("_", "-")
