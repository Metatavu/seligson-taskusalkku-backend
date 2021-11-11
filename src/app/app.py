"""
    Taskusalkku API
"""

from fastapi import FastAPI

from impl.apis.system_api import systemApiRouter
from impl.apis.funds_api import fundsApiRouter

app = FastAPI(
    title="Taskusalkku API",
    description="Taskusalkku API",
    version="1.0.0",
)

app.include_router(systemApiRouter)
app.include_router(fundsApiRouter)
