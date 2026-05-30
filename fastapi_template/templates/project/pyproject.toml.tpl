[project]
name = "$project_name"
version = "0.1.0"
description = "FastAPI application."
requires-python = ">=3.11"
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "pydantic-settings",
]

[dependency-groups]
dev = [
    "pytest",
]
