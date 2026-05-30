from __future__ import annotations

from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def list_$app_name() -> dict[str, str]:
    return {"message": "$app_name app is ready"}
