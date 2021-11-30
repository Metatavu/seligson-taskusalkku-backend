"""
    Taskusalkku API
"""

from fastapi import FastAPI
import os
from impl.apis.system_api import system_api_router
from impl.apis.funds_api import funds_api_router
from impl.apis.meetings_api import meetings_api_router
from fastapi_mail import ConnectionConfig

email_conf = ConnectionConfig(
    MAIL_USERNAME=os.environ["MAIL_USERNAME"],
    MAIL_PASSWORD=os.environ["MAIL_PASSWORD"],
    MAIL_FROM=os.environ["MAIL_FROM"],
    MAIL_PORT=587,
    MAIL_SERVER=os.environ["MAIL_SERVER"],
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

app = FastAPI(
    title="Taskusalkku API",
    description="Taskusalkku API",
    version="1.0.0",
)

app.include_router(system_api_router)
app.include_router(funds_api_router)
app.include_router(meetings_api_router)
