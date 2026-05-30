from __future__ import annotations

import keyword
import re


PACKAGE_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def normalize_package_name(name: str) -> str:
    return name.strip().replace("-", "_").replace(" ", "_").lower()


def validate_package_name(name: str, label: str) -> str:
    if not PACKAGE_RE.match(name) or keyword.iskeyword(name):
        raise ValueError(f"{label} must be a valid Python package name.")
    return name
