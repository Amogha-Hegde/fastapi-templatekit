# fastapi-template
A FastAPI template with a root-level, Django-style app layout.

## Structure

```text
.
├── api/           # top-level router registration
├── health/        # example domain app at project root
├── main/
│   ├── config.py  # settings and config live here
│   └── app.py     # FastAPI declaration lives here
└── pyproject.toml
```

This follows the same domain-first idea from `fastapi-best-practices`, but without a `src/` directory.
Feature apps and the shared API router live directly under the project root, similar to Django apps.

## Run

```bash
uv run uvicorn main.app:app --reload
```

## Add a new app

Create a root-level package such as `users/` or `orders/`, define its router there, and include it from `api/router.py`.
