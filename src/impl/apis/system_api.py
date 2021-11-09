# coding: utf-8

from fastapi_utils.cbv import cbv
from spec.apis.system_api import SystemApiSpec, router as SystemApiRouter
from sqlalchemy.orm import Session
from src.db.database import SessionLocal


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@cbv(SystemApiRouter)
class SystemApiImpl(SystemApiSpec):

    async def ping(self, db: Session = None,) -> str:
        return "pong"
