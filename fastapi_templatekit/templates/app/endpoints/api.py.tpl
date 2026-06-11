from __future__ import annotations

from fastapi import APIRouter

from $app_name.schemas.validator import HelloWorldResponse
from $app_name.service.${app_name}_service import get_hello_world_message


router = APIRouter()


@router.get("/", response_model=HelloWorldResponse)
async def hello_world() -> HelloWorldResponse:
    return HelloWorldResponse(message=get_hello_world_message())
