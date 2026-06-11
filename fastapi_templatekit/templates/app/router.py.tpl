from __future__ import annotations

from fastapi import APIRouter

from $app_name.endpoints.api import router as api_router


router = APIRouter()
router.include_router(api_router)
