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

If generated files already exist, the CLI asks before overwriting them. Use
`--force` to overwrite without a prompt:

```bash
uvx fastapi-template startproject myproject . --force
```

Create the project at a custom path:

```bash
uvx fastapi-template startproject myproject ../services/myproject
```

For local development from this repository:

```bash
uvx --from . fastapi-template startproject myproject
```

Generated projects include a Typer management command to discover registered
HTTP and websocket routes:

```bash
uv run myproject urls
```

Show available commands and details:

```bash
uvx fastapi-template help
```

Add health probes to an existing generated project:

```bash
uvx fastapi-template addhealthprobes
```

Create an app with optional websocket and database scaffolding:

```bash
uvx fastapi-template startapp users
uvx fastapi-template startapp users --with-websockets --with-database
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
    ├── endpoints/
    │   ├── __init__.py
    │   └── api.py
    ├── schemas/
    │   ├── __init__.py
    │   └── validator.py
    ├── service/
    │   ├── __init__.py
    │   └── users_service.py
    ├── models/          # created only with database/tables enabled
    │   └── __init__.py
    └── websocket/       # created only with websockets enabled
        ├── __init__.py
        └── router.py
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
For websocket-related environment configuration, refer to https://github.com/Amogha-Hegde/fastapi-websockets.

Tests force `FASTAPI_WEBSOCKETS_BACKEND=inmemory` so they do not depend on a running database.

Example session:

```text
connect ws://127.0.0.1:8000/api/v1/ws/demo
receive {"event":"connected","room":"demo",...}
send {"sender":"alice","message":"hello"}
receive {"event":"message","room":"demo","sender":"alice","message":"hello"}
```

## Add a new app

Create a root-level package such as `users/` or `orders/`, define its router there, and include it from your project's main `router.py`.
