# coding: utf-8

from typing import Dict, List  # noqa: F401
from abc import ABC, abstractmethod

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
)

from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from ...spec.models.extra_models import TokenModel  # noqa: F401
from spec.models.error import Error
from spec.models.fund import Fund
from spec.models.historical_value import HistoricalValue
from impl.security_api import get_token_bearerAuth

router = APIRouter()
router = InferringRouter()

@cbv(router)
class FundsApiSpec(ABC):


    @abstractmethod
    async def find_fund(self,
        fundId: str = Path(None, description="fund id"),
        token_bearerAuth: TokenModel = Security(
            get_token_bearerAuth
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
    async def find_fund_spec(self,
        fundId: str = Path(None, description="fund id"),
        token_bearerAuth: TokenModel = Security(
            get_token_bearerAuth
        ),
    ) -> Fund:
        """Finds a fund by id."""
        return await self.find_fund(fundId, token_bearerAuth)



    @abstractmethod
    async def list_funds(self,
        first_result: int = Query(None, description="First result. Defaults to 0"),
        max_results: int = Query(None, description="Max results. Defaults to 10"),
        token_bearerAuth: TokenModel = Security(
            get_token_bearerAuth
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
    async def list_funds_spec(self,
        first_result: int = Query(None, description="First result. Defaults to 0"),
        max_results: int = Query(None, description="Max results. Defaults to 10"),
        token_bearerAuth: TokenModel = Security(
            get_token_bearerAuth
        ),
    ) -> List[Fund]:
        """Lists funds."""
        return await self.list_funds(firstResult, maxResults, token_bearerAuth)



    @abstractmethod
    async def list_historical_values(self,
        fundId: str = Path(None, description="fund id"),
        first_result: int = Query(None, description="First result. Defaults to 0"),
        max_results: int = Query(None, description="Max results. Defaults to 10"),
        start_date: str = Query(None, description="Filter starting from this date"),
        end_date: str = Query(None, description="Filter ending to this date"),
        token_bearerAuth: TokenModel = Security(
            get_token_bearerAuth
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
    async def list_historical_values_spec(self,
        fundId: str = Path(None, description="fund id"),
        first_result: int = Query(None, description="First result. Defaults to 0"),
        max_results: int = Query(None, description="Max results. Defaults to 10"),
        start_date: str = Query(None, description="Filter starting from this date"),
        end_date: str = Query(None, description="Filter ending to this date"),
        token_bearerAuth: TokenModel = Security(
            get_token_bearerAuth
        ),
    ) -> List[HistoricalValue]:
        """Lists historical values"""
        return await self.list_historical_values(fundId, firstResult, maxResults, startDate, endDate, token_bearerAuth)
