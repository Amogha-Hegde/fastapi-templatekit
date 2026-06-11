from __future__ import annotations

from fastapi import FastAPI

from $package_name.config import settings
from $package_name.router import api_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(api_router, prefix=settings.api_prefix)
