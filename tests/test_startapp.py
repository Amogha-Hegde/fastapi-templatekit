from __future__ import annotations

import argparse

import pytest

from fastapi_template.commands import startapp


def write_project_files(tmp_path) -> None:
    (tmp_path / "fastapi_template.toml").write_text(
        '[project]\nname = "demo"\npackage = "demo"\napps_dir = "."\n',
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        "\n".join(
            [
                "[project]",
                'name = "demo"',
                "dependencies = [",
                '    "fastapi",',
                "]",
            ]
        ),
        encoding="utf-8",
    )


def test_startapp_with_websockets_uses_class_based_consumer(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    write_project_files(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(startapp, "ask_yes_no", lambda question: False)

    startapp.handle_startapp(
        argparse.Namespace(
            name="chat",
            with_websockets=True,
            with_database=False,
        )
    )

    router_source = (tmp_path / "chat" / "websocket" / "router.py").read_text(
        encoding="utf-8"
    )

    assert "class EchoConsumer(AsyncWebSocketConsumer):" in router_source
    assert "async def connect(self) -> None:" in router_source
    assert "async def receive_text(self, text_data: str) -> None:" in router_source
    assert "async def disconnect(self, close_code: int | None) -> None:" in router_source
    assert 'print("WebSocket disconnected:", close_code)' in router_source
    assert "consumer = EchoConsumer(layer=channel_layer)" in router_source
    assert "del close_code" not in router_source
    assert "WebSocketDisconnect" not in router_source

    pyproject_source = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert '    "fastapi-websockets",' in pyproject_source

    output = capsys.readouterr().out
    assert "Register the websocket router in your project API router:" in output
    assert (
        'api_router.include_router(chat_websocket_router, prefix="/chat")'
        in output
    )
    assert "app.include_router(chat_websocket_router" not in output


def test_startapp_without_websockets_does_not_add_websocket_dependency(
    tmp_path,
    monkeypatch,
) -> None:
    write_project_files(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(startapp, "ask_yes_no", lambda question: False)

    startapp.handle_startapp(
        argparse.Namespace(
            name="billing",
            with_websockets=False,
            with_database=False,
        )
    )

    pyproject_source = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert "fastapi-websockets" not in pyproject_source
    assert not (tmp_path / "billing" / "websocket").exists()


@pytest.mark.parametrize(
    "existing_dependency",
    [
        "fastapi-websockets",
        "fastapi_websockets",
        "fastapi-websockets>=1.0",
        'fastapi-websockets[redis]; python_version >= "3.11"',
    ],
)
def test_startapp_websocket_dependency_is_not_duplicated(
    tmp_path,
    existing_dependency,
) -> None:
    toml_dependency = existing_dependency.replace('"', '\\"')
    (tmp_path / "pyproject.toml").write_text(
        "\n".join(
            [
                "[project]",
                'name = "demo"',
                "dependencies = [",
                '    "fastapi",',
                f'    "{toml_dependency}",',
                "]",
            ]
        ),
        encoding="utf-8",
    )

    startapp.ensure_project_dependency(tmp_path, startapp.WEBSOCKET_DEPENDENCY)

    pyproject_source = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert pyproject_source.count("fastapi-websockets") == (
        1 if "fastapi-websockets" in existing_dependency else 0
    )
    assert pyproject_source.count("fastapi_websockets") == (
        1 if "fastapi_websockets" in existing_dependency else 0
    )


def test_startapp_websocket_dependency_adds_dependencies_array(tmp_path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "\n".join(
            [
                "[project]",
                'name = "demo"',
                'version = "0.1.0"',
            ]
        ),
        encoding="utf-8",
    )

    startapp.ensure_project_dependency(tmp_path, startapp.WEBSOCKET_DEPENDENCY)

    pyproject_source = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert "dependencies = [" in pyproject_source
    assert '    "fastapi-websockets",' in pyproject_source


def test_startapp_websocket_dependency_requires_pyproject(tmp_path) -> None:
    with pytest.raises(SystemExit, match="missing project config"):
        startapp.ensure_project_dependency(tmp_path, startapp.WEBSOCKET_DEPENDENCY)
