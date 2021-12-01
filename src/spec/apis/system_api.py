# coding: utf-8
import os

from functools import lru_cache
from typing import Dict, List, Iterator, Optional  # noqa: F401
from abc import ABC, abstractmethod
from uuid import UUID
from datetime import date

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    Path,
    Query,
    Response,
    Security,
    status,
    HTTPException
)

from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.session import FastAPISessionMaker
from sqlalchemy.orm import Session

from spec.models.extra_models import TokenModel  # noqa: F401


router = InferringRouter()


def get_database() -> Iterator[Session]:
    """FastAPI dependency that provides a sqlalchemy session

    Yields:
        Iterator[Session]: sqlalchemy session
    """
    yield from _get_fastapi_sessionmaker().get_db()


@lru_cache()
def _get_fastapi_sessionmaker() -> FastAPISessionMaker:
    """Returns FastAPI session maker

    Returns:
        FastAPISessionMaker: FastAPI session maker
    """
    database_uri = os.environ["DATABASE_URL"]
    return FastAPISessionMaker(database_uri)


@cbv(router)
class SystemApiSpec(ABC):

    database: Session = Depends(get_database)

    @abstractmethod
    async def ping(
        self,
    ) -> str:
        ...

    @router.get(
        "/v1/system/ping",
        responses={
            200: {"model": str, "description": "Pong"},
        },
        tags=["System"],
        summary="Replies with pong",
    )
    async def ping_spec(
        self,
    ) -> str:
        """Replies ping with pong"""

        return await self.ping(
            
        )

    def to_date(self, isodate: str) -> Optional[date]:
        """Translates given string to date

        Args:
            isodate (str): date as ISO date string

        Raises:
            HTTPException: bad request HTTPException when isodate is not valid ISO date string

        Returns:
            date: parsed date object
        """
        if not isodate:
            return None

        try:
            return date.fromisoformat(isodate)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date {isodate}"
            )

    def to_uuid(self, hexadecimal_uuid: str) -> Optional[UUID]:
        """Translates given hex to UUID

        Args:
            hexadecimal_uuid (str): UUID in hexadecimal string

        Raises:
            HTTPException: bad request HTTPException when hexadecimal_uuid is not valid UUID string

        Returns:
            UUID: UUID
        """
        if not hexadecimal_uuid:
            return None

        try:
            return UUID(hex=hexadecimal_uuid)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid UUID {hexadecimal_uuid}"
            )
