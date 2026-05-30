from __future__ import annotations

import argparse
from pathlib import Path

from fastapi_template.commands.project import load_project_config
from fastapi_template.commands.rendering import render_template


HEALTHPROBES_APP_NAME = "healthprobes"

HEALTHPROBES_TEMPLATES = (
    ("healthprobes/__init__.py.tpl", "healthprobes/__init__.py"),
    ("healthprobes/router.py.tpl", "healthprobes/router.py"),
    ("healthprobes/endpoints/__init__.py.tpl", "healthprobes/endpoints/__init__.py"),
    ("healthprobes/endpoints/api.py.tpl", "healthprobes/endpoints/api.py"),
    ("healthprobes/schemas/__init__.py.tpl", "healthprobes/schemas/__init__.py"),
    ("healthprobes/schemas/validator.py.tpl", "healthprobes/schemas/validator.py"),
    ("healthprobes/service/__init__.py.tpl", "healthprobes/service/__init__.py"),
    ("healthprobes/service/healthprobes_service.py.tpl", "healthprobes/service/healthprobes_service.py"),
    ("healthprobes/models/__init__.py.tpl", "healthprobes/models/__init__.py"),
)


def add_addhealthprobes_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "addhealthprobes",
        help="Add healthz and livez endpoints to an existing generated project.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing healthprobes files without prompting.",
    )
    parser.set_defaults(handler=handle_addhealthprobes)


def handle_addhealthprobes(args: argparse.Namespace) -> None:
    project_root = Path.cwd()
    project = load_project_config(project_root)
    apps_dir = project_root / project.get("apps_dir", ".")
    app_dir = apps_dir / HEALTHPROBES_APP_NAME

    context = {
        "app_name": HEALTHPROBES_APP_NAME,
        "route_prefix": HEALTHPROBES_APP_NAME,
    }
    destinations = [
        apps_dir / destination_pattern.format(**context)
        for _, destination_pattern in HEALTHPROBES_TEMPLATES
    ]
    existing_paths = [destination for destination in destinations if destination.exists()]

    if existing_paths and not args.force:
        conflicts = "\n".join(f"  {path}" for path in existing_paths)
        print(f"Healthprobes files already exist:\n{conflicts}")
        answer = input("Overwrite these files? [y/N]: ").strip().lower()
        if answer not in {"y", "yes"}:
            raise SystemExit("Aborted.")

    for template_path, destination_pattern in HEALTHPROBES_TEMPLATES:
        destination = apps_dir / destination_pattern.format(**context)
        render_template(template_path, destination, context)

    print(f"Created health probes app at {app_dir}")
    print("Register the router in your project router:")
    print("  from healthprobes.router import router as healthprobes_router")
    print("  api_router.include_router(healthprobes_router, tags=[\"healthprobes\"])")
