from __future__ import annotations

from pydantic import BaseModel


class ${app_class_name}Response(BaseModel):
    message: str
