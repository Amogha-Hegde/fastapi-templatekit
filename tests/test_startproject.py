from __future__ import annotations

import argparse
import ast
from collections.abc import Iterable

from fastapi_templatekit.commands import startproject


def test_startproject_generates_gitignore_for_python_build_artifacts(tmp_path) -> None:
    target_dir = tmp_path / "demo"

    startproject.handle_startproject(
        argparse.Namespace(
            name="demo",
            directory=str(target_dir),
            force=False,
        )
    )

    gitignore = (target_dir / ".gitignore").read_text(encoding="utf-8")

    assert "*.egg-info/" in gitignore
    assert ".venv/" in gitignore
    assert "__pycache__/" in gitignore


def test_generated_urls_command_traverses_included_router_tree(tmp_path) -> None:
    target_dir = tmp_path / "demo"

    startproject.handle_startproject(
        argparse.Namespace(
            name="demo",
            directory=str(target_dir),
            force=False,
        )
    )

    namespace = load_generated_route_helpers(target_dir / "demo" / "cli.py")

    class Route:
        def __init__(self, path: str, methods: set[str] | None = None) -> None:
            self.path = path
            self.methods = methods

    class APIRoute(Route):
        pass

    class APIWebSocketRoute:
        def __init__(self, path: str) -> None:
            self.path = path

    class WebSocketRoute:
        def __init__(self, path: str) -> None:
            self.path = path

    class Mount:
        def __init__(self, path: str, routes: list[object]) -> None:
            self.path = path
            self.routes = routes

    class Router:
        def __init__(self, routes: list[object]) -> None:
            self.routes = routes

    class IncludeContext:
        def __init__(self, prefix: str) -> None:
            self.prefix = prefix

    class IncludedRouter:
        def __init__(self, original_router: Router, prefix: str) -> None:
            self.original_router = original_router
            self.include_context = IncludeContext(prefix)

    namespace.update(
        {
            "APIRoute": APIRoute,
            "APIWebSocketRoute": APIWebSocketRoute,
            "Route": Route,
            "WebSocketRoute": WebSocketRoute,
            "Mount": Mount,
        }
    )

    nested_router = Router([APIRoute("/healthz", {"GET"})])
    api_router = Router(
        [
            IncludedRouter(nested_router, "/health"),
            APIWebSocketRoute("/events"),
        ]
    )
    routes = [
        IncludedRouter(api_router, "/api/v1"),
        Mount("/mounted", [Route("/status", {"HEAD", "GET"})]),
    ]

    assert list(namespace["iter_routes"](routes)) == [
        ("HTTP", "GET", "/api/v1/health/healthz"),
        ("WEBSOCKET", "WS", "/api/v1/events"),
        ("HTTP", "GET, HEAD", "/mounted/status"),
    ]


def load_generated_route_helpers(cli_path):
    module = ast.parse(cli_path.read_text(encoding="utf-8"))
    helper_nodes = [
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef)
        and node.name in {"iter_routes", "normalize_path"}
    ]
    namespace = {"Iterable": Iterable}
    exec(compile(ast.Module(body=helper_nodes, type_ignores=[]), str(cli_path), "exec"), namespace)
    return namespace
