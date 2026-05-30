# fastapi-template
A FastAPI template with a root-level, Django-style app layout.

## CLI

Create a new project without installing this template into that project's
environment:

```bash
uvx fastapi-template startproject myproject
cd myproject
uvx fastapi-template startapp users
```

Create the project files directly in the current directory:

```bash
uvx fastapi-template startproject myproject .
```

Create the project at a custom path:

```bash
uvx fastapi-template startproject myproject ../services/myproject
```

For local development from this repository:

```bash
uvx --from . fastapi-template startproject myproject
```

Generated projects keep the main router beside `main.py`:

```text
myproject/
├── pyproject.toml
├── fastapi_template.toml
├── myproject/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   └── router.py
└── users/
    ├── __init__.py
    ├── router.py
    ├── schemas.py
    ├── service.py
    └── models.py
```

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

## WebSockets

WebSocket routes are mounted under the same API prefix, so the default endpoint is:

```text
/api/v1/ws/{room_name}
```

There is also a built-in browser test page at:

```text
/api/v1/ws/test
```

This app uses `fastapi-websockets` with the package's environment-based channel-layer loader.

For PostgreSQL, configure:

```text
FASTAPI_WEBSOCKETS_BACKEND=postgresql
FASTAPI_WEBSOCKETS_POSTGRESQL_DSN=postgresql://db:pass%40123@localhost:5432/db
```

Tests force `FASTAPI_WEBSOCKETS_BACKEND=inmemory` so they do not depend on a running database.

Example session:

```text
connect ws://127.0.0.1:8000/api/v1/ws/demo
receive {"event":"connected","room":"demo",...}
send {"sender":"alice","message":"hello"}
receive {"event":"message","room":"demo","sender":"alice","message":"hello"}
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

Create a root-level package such as `users/` or `orders/`, define its router there, and include it from your project's main `router.py`.
