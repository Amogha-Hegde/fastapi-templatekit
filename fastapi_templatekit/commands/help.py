from __future__ import annotations

import argparse


HELP_TEXT = """fastapi-templatekit

Available commands:

  startproject <name> [directory]
    Create a new FastAPI project.

    Examples:
      fastapi-templatekit startproject myproject
      fastapi-templatekit startproject myproject .
      fastapi-templatekit startproject myproject ../services/myproject

    Details:
      - Without directory, creates ./<name>/.
      - With '.', creates project files in the current directory.
      - With a custom directory, creates project files at that path.
      - If generated files already exist, asks before overwriting.
      - Use --force to overwrite generated files without prompting.

  startapp <name>
    Create a root-level app inside an existing generated project.

    Example:
      fastapi-templatekit startapp users
      fastapi-templatekit startapp users --with-websockets --with-database

    Details:
      - Must be run from a directory containing fastapi_templatekit.toml.
      - Creates endpoints, schemas, service, and router.py.
      - Includes a hello-world GET endpoint.
      - Asks whether to include websockets.
      - Asks whether to include database/tables.
      - Use --with-websockets to add websocket scaffolding without prompting for it.
      - Use --with-database to add the models folder without prompting for it.
      - Prints the router registration lines for your project router.py.

  addhealthprobes
    Create a root-level healthprobes app inside an existing generated project.

    Example:
      fastapi-templatekit addhealthprobes

    Details:
      - Must be run from a directory containing fastapi_templatekit.toml.
      - Creates /healthz and /livez GET endpoints.
      - Prints the router registration lines for your project router.py.
      - Use --force to overwrite generated healthprobes files without prompting.

  help
    Show this command summary.

Use 'fastapi-templatekit <command> --help' for argparse usage details.
"""


def add_help_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "help",
        help="Show available commands and details.",
    )
    parser.set_defaults(handler=handle_help)


def handle_help(_: argparse.Namespace) -> None:
    print(HELP_TEXT)
