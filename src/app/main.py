# coding: utf-8

"""
    Taskusalkku API
"""

from fastapi import FastAPI

from ..impl.apis.system_api import SystemApiRouter

app = FastAPI(
    title="Taskusalkku API",
    description="Taskusalkku API",
    version="1.0.0",
)

app.include_router(SystemApiRouter)
