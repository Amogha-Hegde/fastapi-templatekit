from __future__ import annotations

from pydantic import BaseModel


class HelloWorldResponse(BaseModel):
    message: str
