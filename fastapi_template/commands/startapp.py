from __future__ import annotations

import argparse
import tomllib
from pathlib import Path

from fastapi_template.commands.rendering import render_template
from fastapi_template.commands.validation import normalize_package_name, validate_package_name


APP_TEMPLATES = (
    ("app/__init__.py.tpl", "{app_name}/__init__.py"),
    ("app/router.py.tpl", "{app_name}/router.py"),
    ("app/endpoints/__init__.py.tpl", "{app_name}/endpoints/__init__.py"),
    ("app/endpoints/api.py.tpl", "{app_name}/endpoints/api.py"),
    ("app/schemas/__init__.py.tpl", "{app_name}/schemas/__init__.py"),
    ("app/schemas/validator.py.tpl", "{app_name}/schemas/validator.py"),
    ("app/service/__init__.py.tpl", "{app_name}/service/__init__.py"),
    ("app/service/app_service.py.tpl", "{app_name}/service/{app_name}_service.py"),
    ("app/models/__init__.py.tpl", "{app_name}/models/__init__.py"),
)


def add_startapp_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "startapp",
        help="Create a FastAPI app inside an existing generated project.",
    )
    parser.add_argument("name", help="App name.")
    parser.set_defaults(handler=handle_startapp)


def handle_startapp(args: argparse.Namespace) -> None:
    project_root = Path.cwd()
    marker_path = project_root / "fastapi_template.toml"

    if not marker_path.exists():
        raise SystemExit(
            "Error: startapp must be run inside a fastapi-template project.\n"
            "Run: fastapi-template startproject <project_name>"
        )

    marker = tomllib.loads(marker_path.read_text(encoding="utf-8"))
    project = marker.get("project", {})
    apps_dir = project_root / project.get("apps_dir", ".")

    app_name = validate_package_name(
        normalize_package_name(args.name),
        "App name",
    )
    app_dir = apps_dir / app_name

    if app_dir.exists():
        raise SystemExit(f"Error: app already exists: {app_dir}")

    context = {
        "app_name": app_name,
        "app_class_name": "".join(part.capitalize() for part in app_name.split("_")),
        "route_prefix": app_name.replace("_", "-"),
    }

    for template_path, destination_pattern in APP_TEMPLATES:
        destination = apps_dir / destination_pattern.format(**context)
        render_template(template_path, destination, context)

    print(f"Created FastAPI app '{app_name}' at {app_dir}")
    print("Register the router in your project API router:")
    print(f"  from {app_name}.router import router as {app_name}_router")
    print(f"  api_router.include_router({app_name}_router, prefix=\"/{context['route_prefix']}\", tags=[\"{app_name}\"])")
