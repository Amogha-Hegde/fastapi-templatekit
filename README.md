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

## Docker

Build the production image:

```bash
docker build -f deployment/Dockerfile -t fastapi-template .
```

Build with optional dependency groups from `pyproject.toml`:

```bash
docker build -f deployment/Dockerfile --build-arg INSTALL_EXTRAS=postgres -t fastapi-template .
```

Run it:

```bash
docker run --rm -p 8000:8000 fastapi-template
```

The Docker image is multi-stage, uses a non-root runtime user, and keeps the runtime image minimal.
Dependencies are installed from `pyproject.toml` with `uv`, and optional groups can be selected with `INSTALL_EXTRAS`.
If you enable extras like `mysqlclient` or `psycopg`, you will likely need to extend the Dockerfile with the required OS-level client libraries.

## Add a new app

Create a root-level package such as `users/` or `orders/`, define its router there, and include it from `api/router.py`.
