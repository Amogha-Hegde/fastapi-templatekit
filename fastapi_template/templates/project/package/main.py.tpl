from __future__ import annotations

from fastapi import FastAPI

from $package_name.api.router import api_router
from $package_name.config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(api_router, prefix=settings.api_prefix)
