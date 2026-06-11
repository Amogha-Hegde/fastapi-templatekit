from __future__ import annotations

import sys
from collections.abc import Iterable
from pathlib import Path

import typer
from fastapi.routing import APIRoute, APIWebSocketRoute
from starlette.routing import Mount, Route, WebSocketRoute

project_root = str(Path.cwd())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from $package_name.main import app as fastapi_app


app = typer.Typer(help="Project management commands.")


@app.callback()
def main() -> None:
    """Project management commands."""


@app.command("urls")
def discover_urls() -> None:
    """List HTTP and websocket routes registered on the FastAPI app."""
    rows = list(iter_routes(fastapi_app.routes))

    if not rows:
        typer.echo("No routes found.")
        return

    protocol_width = max(len(row[0]) for row in rows + [("Protocol", "", "")])
    methods_width = max(len(row[1]) for row in rows + [("Protocol", "Methods", "")])
    path_width = max(len(row[2]) for row in rows + [("Protocol", "Methods", "Path")])

    typer.echo(
        f"{'Protocol'.ljust(protocol_width)}  "
        f"{'Methods'.ljust(methods_width)}  "
        f"{'Path'.ljust(path_width)}"
    )
    typer.echo(
        f"{'-' * protocol_width}  "
        f"{'-' * methods_width}  "
        f"{'-' * path_width}"
    )

    for protocol, methods, path in rows:
        typer.echo(
            f"{protocol.ljust(protocol_width)}  "
            f"{methods.ljust(methods_width)}  "
            f"{path.ljust(path_width)}"
        )


def iter_routes(routes: Iterable[Route], prefix: str = "") -> Iterable[tuple[str, str, str]]:
    for route in routes:
        path = normalize_path(prefix, getattr(route, "path", ""))

        if isinstance(route, APIRoute):
            methods = ", ".join(sorted(route.methods or []))
            yield ("HTTP", methods, path)
            continue

        if isinstance(route, Route):
            methods = ", ".join(sorted(route.methods or []))
            yield ("HTTP", methods, path)
            continue

        if isinstance(route, APIWebSocketRoute | WebSocketRoute):
            yield ("WEBSOCKET", "WS", path)
            continue

        if isinstance(route, Mount):
            yield from iter_routes(route.routes, path)


def normalize_path(prefix: str, path: str) -> str:
    combined = f"{prefix.rstrip('/')}/{path.lstrip('/')}"
    if not combined.startswith("/"):
        combined = f"/{combined}"
    return combined.rstrip("/") or "/"


if __name__ == "__main__":
    app()
