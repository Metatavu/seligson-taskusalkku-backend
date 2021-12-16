"""
    Taskusalkku API
"""

from fastapi import FastAPI

from impl.apis.system_api import system_api_router
from impl.apis.funds_api import funds_api_router
from impl.apis.meetings_api import meetings_api_router
from impl.apis.portfolios_api import portfolios_api_router
from impl.apis.securities_api import securities_api_router

app = FastAPI(
    title="Taskusalkku API",
    description="Taskusalkku API",
    version="1.0.0",
)

app.include_router(system_api_router)
app.include_router(funds_api_router)
app.include_router(securities_api_router)
app.include_router(meetings_api_router)
app.include_router(portfolios_api_router)
