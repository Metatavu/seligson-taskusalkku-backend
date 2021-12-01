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
from spec.models.error import Error
from spec.models.fund import Fund
from spec.models.historical_value import HistoricalValue
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
    database_uri = os.environ["DATABASE_URL"]
    return FastAPISessionMaker(database_uri)


@cbv(router)
class FundsApiSpec(ABC):

    database: Session = Depends(get_database)

    @abstractmethod
    async def find_fund(
        self,
        fund_id: UUID,
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> Fund:
        ...

    @router.get(
        "/v1/funds/{fundId}",
        responses={
            200: {"model": Fund, "description": "Fund"},
            400: {"model": Error, "description": "Invalid request was sent to the server"},
            403: {"model": Error, "description": "Attempted to make a call with unauthorized client"},
            500: {"model": Error, "description": "Internal server error"},
        },
        tags=["Funds"],
        summary="Find a fund.",
    )
    async def find_fund_spec(
        self,
        fund_id: str = Path(None, description="fund id", alias="fundId"),
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> Fund:
        """Finds a fund by id."""

        if fund_id is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter fundId"
            )

        return await self.find_fund(
            fund_id=self.to_uuid(fund_id),
            token_bearer=token_bearer
        )

    @abstractmethod
    async def list_funds(
        self,
        first_result: int,
        max_results: int,
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> List[Fund]:
        ...

    @router.get(
        "/v1/funds",
        responses={
            200: {"model": List[Fund], "description": "List of funds"},
            400: {"model": Error, "description": "Invalid request was sent to the server"},
            403: {"model": Error, "description": "Attempted to make a call with unauthorized client"},
            500: {"model": Error, "description": "Internal server error"},
        },
        tags=["Funds"],
        summary="List funds.",
    )
    async def list_funds_spec(
        self,
        first_result: int = Query(None, description="First result. Defaults to 0", alias="firstResult"),
        max_results: int = Query(None, description="Max results. Defaults to 10", alias="maxResults"),
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> List[Fund]:
        """Lists funds."""

        return await self.list_funds(
            first_result=first_result,
            max_results=max_results,
            token_bearer=token_bearer
        )

    @abstractmethod
    async def list_historical_values(
        self,
        fund_id: UUID,
        first_result: int,
        max_results: int,
        start_date: date,
        end_date: date,
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> List[HistoricalValue]:
        ...

    @router.get(
        "/v1/funds/{fundId}/historicalValues",
        responses={
            200: {"model": List[HistoricalValue], "description": "List of historical values"},
            400: {"model": Error, "description": "Invalid request was sent to the server"},
            403: {"model": Error, "description": "Attempted to make a call with unauthorized client"},
            500: {"model": Error, "description": "Internal server error"},
        },
        tags=["Funds"],
        summary="Lists historical values",
    )
    async def list_historical_values_spec(
        self,
        fund_id: str = Path(None, description="fund id", alias="fundId"),
        first_result: int = Query(None, description="First result. Defaults to 0", alias="firstResult"),
        max_results: int = Query(None, description="Max results. Defaults to 10", alias="maxResults"),
        start_date: str = Query(None, description="Filter starting from this date", alias="startDate"),
        end_date: str = Query(None, description="Filter ending to this date", alias="endDate"),
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> List[HistoricalValue]:
        """Lists historical values"""

        if fund_id is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter fundId"
            )

        return await self.list_historical_values(
            fund_id=self.to_uuid(fund_id),
            first_result=first_result,
            max_results=max_results,
            start_date=self.to_date(start_date),
            end_date=self.to_date(end_date),
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
