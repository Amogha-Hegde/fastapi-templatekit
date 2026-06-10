from __future__ import annotations

import argparse
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
