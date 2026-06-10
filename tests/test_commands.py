from __future__ import annotations

import argparse
import sys

import pytest

from fastapi_template import cli
from fastapi_template.commands import addhealthprobes, help as help_command, project
from fastapi_template.commands import startapp, startproject
from fastapi_template.commands.validation import normalize_package_name, validate_package_name


def test_build_parser_registers_commands() -> None:
    parser = cli.build_parser()

    command_args = (
        ["startproject", "demo"],
        ["startapp", "users"],
        ["addhealthprobes"],
        ["help"],
    )
    for command in command_args:
        args = parser.parse_args(command)
        assert args is not None


def test_main_dispatches_selected_handler(monkeypatch) -> None:
    called = {}

    def fake_build_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        parser.set_defaults(handler=lambda args: called.setdefault("args", args))
        return parser

    monkeypatch.setattr(cli, "build_parser", fake_build_parser)
    monkeypatch.setattr(sys, "argv", ["fastapi-template"])

    cli.main()

    assert "args" in called


def test_help_command_prints_summary(capsys) -> None:
    help_command.handle_help(argparse.Namespace())

    output = capsys.readouterr().out
    assert "startproject <name>" in output
    assert "startapp <name>" in output
    assert "addhealthprobes" in output


def test_project_config_errors(tmp_path) -> None:
    with pytest.raises(SystemExit, match="must be run inside"):
        project.load_project_config(tmp_path)

    (tmp_path / "fastapi_template.toml").write_text(
        'project = "invalid"\n',
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="invalid project config"):
        project.load_project_config(tmp_path)


def test_validation_normalizes_and_rejects_invalid_names() -> None:
    assert normalize_package_name(" My-App ") == "my_app"
    assert validate_package_name("valid_name", "Project name") == "valid_name"

    with pytest.raises(ValueError, match="valid Python package name"):
        validate_package_name("class", "Project name")

    with pytest.raises(ValueError, match="valid Python package name"):
        validate_package_name("invalid-name", "Project name")


def test_startproject_refuses_file_target(tmp_path) -> None:
    target = tmp_path / "demo"
    target.write_text("not a directory", encoding="utf-8")

    with pytest.raises(SystemExit, match="not a directory"):
        startproject.handle_startproject(
            argparse.Namespace(name="demo", directory=str(target), force=False)
        )


def test_startproject_existing_files_prompt_can_abort(tmp_path, monkeypatch) -> None:
    target = tmp_path / "demo"
    target.mkdir()
    (target / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    monkeypatch.setattr("builtins.input", lambda prompt: "n")

    with pytest.raises(SystemExit, match="Aborted"):
        startproject.handle_startproject(
            argparse.Namespace(name="demo", directory=str(target), force=False)
        )


def test_addhealthprobes_generates_app_and_registration_output(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    (tmp_path / "fastapi_template.toml").write_text(
        '[project]\nname = "demo"\napps_dir = "."\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    addhealthprobes.handle_addhealthprobes(argparse.Namespace(force=False))

    assert (tmp_path / "healthprobes" / "router.py").exists()
    assert (tmp_path / "healthprobes" / "endpoints" / "api.py").exists()
    output = capsys.readouterr().out
    assert "api_router.include_router(healthprobes_router" in output


def test_addhealthprobes_existing_files_prompt_can_abort(tmp_path, monkeypatch) -> None:
    (tmp_path / "fastapi_template.toml").write_text(
        '[project]\nname = "demo"\napps_dir = "."\n',
        encoding="utf-8",
    )
    existing = tmp_path / "healthprobes"
    existing.mkdir()
    (existing / "__init__.py").write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("builtins.input", lambda prompt: "n")

    with pytest.raises(SystemExit, match="Aborted"):
        addhealthprobes.handle_addhealthprobes(argparse.Namespace(force=False))


def test_startapp_dependency_reports_invalid_project_config(tmp_path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "\n".join(
            [
                "[tool.demo]",
                'name = "demo"',
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="invalid project config"):
        startapp.ensure_project_dependency(tmp_path, startapp.WEBSOCKET_DEPENDENCY)
