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
    Security as FastAPISecurity,
    status,
    HTTPException
)

from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.session import FastAPISessionMaker
from sqlalchemy.orm import Session

from spec.models.extra_models import TokenModel  # noqa: F401
from spec.models.error import Error
from spec.models.security import Security
from impl.security_api import get_token_bearer

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
    database_uri = os.environ["BACKEND_DATABASE_URL"]
    return FastAPISessionMaker(database_uri)


@cbv(router)
class SecuritiesApiSpec(ABC):

    database: Session = Depends(get_database)

    @abstractmethod
    async def find_security(
        self,
        security_id: UUID,
        token_bearer: TokenModel,
    ) -> Security:
        ...

    @router.get(
        "/v1/securities/{securityId}",
        responses={
            200: {"model": Security, "description": "Security"},
            400: {"model": Error, "description": "Invalid request was sent to the server"},
            403: {"model": Error, "description": "Attempted to make a call with unauthorized client"},
            500: {"model": Error, "description": "Internal server error"},
        },
        tags=["Securities"],
        summary="Find a security.",
    )
    async def find_security_spec(
        self,
        security_id: str = Path(None, description="security id", alias="securityId"),
        token_bearer: TokenModel = FastAPISecurity(
            get_token_bearer
        ),
    ) -> Security:
        """Finds a security by id."""

        if security_id is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter securityId"
            )

        return await self.find_security(
            security_id=self.to_uuid(security_id),
            token_bearer=token_bearer
        )

    @abstractmethod
    async def list_securities(
        self,
        first_result: Optional[int],
        max_results: Optional[int],
        token_bearer: TokenModel,
    ) -> List[Security]:
        ...

    @router.get(
        "/v1/securities",
        responses={
            200: {"model": List[Security], "description": "List of securities"},
            400: {"model": Error, "description": "Invalid request was sent to the server"},
            403: {"model": Error, "description": "Attempted to make a call with unauthorized client"},
            500: {"model": Error, "description": "Internal server error"},
        },
        tags=["Securities"],
        summary="List securities.",
    )
    async def list_securities_spec(
        self,
        first_result: int = Query(None, description="First result. Defaults to 0", alias="firstResult"),
        max_results: int = Query(None, description="Max results. Defaults to 10", alias="maxResults"),
        token_bearer: TokenModel = FastAPISecurity(
            get_token_bearer
        ),
    ) -> List[Security]:
        """Lists securities."""

        return await self.list_securities(
            first_result=first_result,
            max_results=max_results,
            token_bearer=token_bearer
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
