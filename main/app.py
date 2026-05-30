from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.router import api_router
from main.config import settings
from websocket.router import channel_layer


@asynccontextmanager
async def lifespan(_: FastAPI):
    print(
        "WebSocket backend:",
        f"{channel_layer.__class__.__module__}.{channel_layer.__class__.__name__}",
    )
    try:
        yield
    finally:
        await channel_layer.close()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(api_router, prefix=settings.api_prefix)
