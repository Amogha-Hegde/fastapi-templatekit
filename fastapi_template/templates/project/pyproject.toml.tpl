[project]
name = "$project_name"
version = "0.1.0"
description = "FastAPI application."
requires-python = ">=3.11"
dependencies = [
    "fastapi",
    "typer",
    "uvicorn[standard]",
    "pydantic-settings",
]

[project.scripts]
$package_name = "$package_name.cli:app"

[dependency-groups]
dev = [
    "pytest",
]
