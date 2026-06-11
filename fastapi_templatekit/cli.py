from __future__ import annotations

import argparse

from fastapi_templatekit.commands.addhealthprobes import add_addhealthprobes_parser
from fastapi_templatekit.commands.help import add_help_parser
from fastapi_templatekit.commands.startapp import add_startapp_parser
from fastapi_templatekit.commands.startproject import add_startproject_parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fastapi-templatekit",
        description="Create FastAPI projects and apps.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_startproject_parser(subparsers)
    add_startapp_parser(subparsers)
    add_addhealthprobes_parser(subparsers)
    add_help_parser(subparsers)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
