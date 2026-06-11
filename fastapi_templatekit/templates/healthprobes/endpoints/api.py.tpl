from __future__ import annotations

from fastapi import APIRouter

from healthprobes.schemas.validator import HealthProbeResponse
from healthprobes.service.healthprobes_service import get_health_status


router = APIRouter()


@router.get("/healthz", response_model=HealthProbeResponse)
async def healthz() -> HealthProbeResponse:
    return HealthProbeResponse(status=get_health_status())


@router.get("/livez", response_model=HealthProbeResponse)
async def livez() -> HealthProbeResponse:
    return HealthProbeResponse(status=get_health_status())
