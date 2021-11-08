"""
    Taskusalkku API
"""

from fastapi import FastAPI

from impl.apis.system_api import SystemApiRouter
from impl.apis.funds_api import FundsApiRouter

app = FastAPI(
    title="Taskusalkku API",
    description="Taskusalkku API",
    version="1.0.0",
)

app.include_router(SystemApiRouter)
app.include_router(FundsApiRouter)
