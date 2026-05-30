from fastapi import APIRouter

from health.router import router as health_router
from websocket.router import router as websocket_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(websocket_router)
