# coding: utf-8
import os

from functools import lru_cache
from typing import Dict, List, Iterator  # noqa: F401
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
from spec.models.portfolio import Portfolio
from spec.models.portfolio_fund import PortfolioFund
from spec.models.portfolio_history_value import PortfolioHistoryValue
from spec.models.portfolio_summary import PortfolioSummary
from spec.models.portfolio_transaction import PortfolioTransaction
from spec.models.transaction_type import TransactionType
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
    database_uri = os.environ["SQLALCHEMY_DATABASE_URL"]
    return FastAPISessionMaker(database_uri)


@cbv(router)
class PortfoliosApiSpec(ABC):
    database: Session = Depends(get_database)

    @abstractmethod
    async def find_portfolio(
            self,
            portfolioId: UUID,
            token_bearer: TokenModel = Security(
                get_token_bearer
            ),
    ) -> Portfolio:
        ...

    @router.get(
        "/v1/portfolios/{portfolioId}",
        responses={
            200: {"model": Portfolio, "description": "Portfolio"},
            400: {"model": Error, "description": "Invalid request was sent to the server"},
            403: {"model": Error, "description": "Attempted to make a call with unauthorized client"},
            500: {"model": Error, "description": "Internal server error"},
        },
        tags=["Portfolios"],
        summary="Find a portfolio.",
    )
    async def find_portfolio_spec(
            self,
            portfolioId: str = Path(None, description="portfolio id", alias="portfolioId"),
            token_bearer: TokenModel = Security(
                get_token_bearer
            ),
    ) -> Portfolio:
        """Finds a portfolio by id."""
        return await self.find_portfolio(
            self.to_uuid(portfolioId),
            token_bearer
        )

    @abstractmethod
    async def find_portfolio_transactions(
        self,
        portfolioId: UUID,
        transactionId: UUID,
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> PortfolioTransaction:
        ...

    @router.get(
        "/v1/portfolios/{portfolioId}/transactions/{transactionId}",
        responses={
            200: {"model": PortfolioTransaction, "description": "Found portfolio transaction"},
            400: {"model": Error, "description": "Invalid request was sent to the server"},
            403: {"model": Error, "description": "Attempted to make a call with unauthorized client"},
            404: {"model": Error, "description": "Not found"},
            500: {"model": Error, "description": "Internal server error"},
        },
        tags=["Portfolios"],
        summary="Finds portfolio transactions",
    )
    async def find_portfolio_transactions_spec(
        self,
        portfolioId: str = Path(None, description="Portfolio id", alias="portfolioId"),
        transactionId: str = Path(None, description="Transaction id", alias="transactionId"),
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> PortfolioTransaction:
        """Returns found portfolio transaction"""
        return await self.find_portfolio_transactions(
            self.to_uuid(portfolioId),
            self.to_uuid(transactionId),
            token_bearer
        )

    @abstractmethod
    async def get_portfolio_h_summary(
        self,
        portfolioId: UUID,
        start_date: date,
        end_date: date,
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> PortfolioSummary:
        ...

    @router.get(
        "/v1/portfolios/{portfolioId}/summary",
        responses={
            200: {"model": PortfolioSummary, "description": "Portfolio"},
            400: {"model": Error, "description": "Invalid request was sent to the server"},
            403: {"model": Error, "description": "Attempted to make a call with unauthorized client"},
            500: {"model": Error, "description": "Internal server error"},
        },
        tags=["Portfolios"],
        summary="Summary for portfolio summary",
    )
    async def get_portfolio_h_summary_spec(
        self,
        portfolioId: str = Path(None, description="portfolio id", alias="portfolioId"),
        start_date: str = Query(None, description="Start date for the date range", alias="startDate"),
        end_date: str = Query(None, description="End date for the date range", alias="endDate"),
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> PortfolioSummary:
        """Returns summary a portfolio history for given time range"""
        return await self.get_portfolio_h_summary(
            self.to_uuid(portfolioId),
            self.to_date(start_date),
            self.to_date(end_date),
            token_bearer
        )

    @abstractmethod
    async def list_portfolio_funds(
        self,
        portfolioId: UUID,
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> List[PortfolioFund]:
        ...

    @router.get(
        "/v1/portfolios/{portfolioId}/funds",
        responses={
            200: {"model": List[PortfolioFund], "description": "List of portfolio funds"},
            400: {"model": Error, "description": "Invalid request was sent to the server"},
            403: {"model": Error, "description": "Attempted to make a call with unauthorized client"},
            404: {"model": Error, "description": "Not found"},
            500: {"model": Error, "description": "Internal server error"},
        },
        tags=["Portfolios"],
        summary="Lists portfolio funds",
    )
    async def list_portfolio_funds_spec(
        self,
        portfolioId: str = Path(None, description="portfolio id", alias="portfolioId"),
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> List[PortfolioFund]:
        """Returns list of portfolio funds"""
        return await self.list_portfolio_funds(
            self.to_uuid(portfolioId),
            token_bearer
        )

    @abstractmethod
    async def list_portfolio_history_values(
        self,
        portfolioId: UUID,
        start_date: date,
        end_date: date,
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> List[PortfolioHistoryValue]:
        ...

    @router.get(
        "/v1/portfolios/{portfolioId}/historyValues",
        responses={
            200: {"model": List[PortfolioHistoryValue], "description": "List of portfolio history values"},
            400: {"model": Error, "description": "Invalid request was sent to the server"},
            403: {"model": Error, "description": "Attempted to make a call with unauthorized client"},
            500: {"model": Error, "description": "Internal server error"},
        },
        tags=["Portfolios"],
        summary="List portfolio history values.",
    )
    async def list_portfolio_history_values_spec(
        self,
        portfolioId: str = Path(None, description="portfolio id", alias="portfolioId"),
        start_date: str = Query(None, description="Start date for the date range", alias="startDate"),
        end_date: str = Query(None, description="End date for the date range", alias="endDate"),
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> List[PortfolioHistoryValue]:
        """Lists portfolio history values"""
        return await self.list_portfolio_history_values(
            self.to_uuid(portfolioId),
            self.to_date(start_date),
            self.to_date(end_date),
            token_bearer
        )

    @abstractmethod
    async def list_portfolio_transactions(
        self,
        portfolioId: UUID,
        start_date: date,
        end_date: date,
        type: ,
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> List[PortfolioTransaction]:
        ...

    @router.get(
        "/v1/portfolios/{portfolioId}/transactions",
        responses={
            200: {"model": List[PortfolioTransaction], "description": "List of portfolio transactions"},
            400: {"model": Error, "description": "Invalid request was sent to the server"},
            403: {"model": Error, "description": "Attempted to make a call with unauthorized client"},
            404: {"model": Error, "description": "Not found"},
            500: {"model": Error, "description": "Internal server error"},
        },
        tags=["Portfolios"],
        summary="Lists portfolio transactions",
    )
    async def list_portfolio_transactions_spec(
        self,
        portfolioId: str = Path(None, description="portfolio id", alias="portfolioId"),
        start_date: str = Query(None, description="Start date for the date range", alias="startDate"),
        end_date: str = Query(None, description="End date for the date range", alias="endDate"),
        type:  = Query(None, description="Transaction type", alias="type"),
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> List[PortfolioTransaction]:
        """Returns list of portfolio transactions"""
        return await self.list_portfolio_transactions(
            self.to_uuid(portfolioId),
            self.to_date(start_date),
            self.to_date(end_date),
            type,
            token_bearer
        )

    @abstractmethod
    async def list_portfolios(
        self,
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> List[Portfolio]:
        ...

    @router.get(
        "/v1/portfolios",
        responses={
            200: {"model": List[Portfolio], "description": "List of portfolios"},
            400: {"model": Error, "description": "Invalid request was sent to the server"},
            403: {"model": Error, "description": "Attempted to make a call with unauthorized client"},
            500: {"model": Error, "description": "Internal server error"},
        },
        tags=["Portfolios"],
        summary="List portfolios.",
    )
    async def list_portfolios_spec(
        self,
        token_bearer: TokenModel = Security(
            get_token_bearer
        ),
    ) -> List[Portfolio]:
        """Lists portfolios logged user has access to"""
        return await self.list_portfolios(
            token_bearer
        )

    def to_date(self, isodate: str) -> date:
        """Translates given string to date

        Args:
            isodate (str): date as ISO date string

        Raises:
            HTTPException: bad request HTTPException when isodate is not valid ISO date string

        Returns:
            date: parsed date object
        """
        try:
            return date.fromisoformat(isodate)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date {isodate}"
            )

    def to_uuid(self, hexadecimal_uuid: str) -> UUID:
        """Translates given hex to UUID

        Args:
            hexadecimal_uuid (str): UUID in hexadecimal string

        Raises:
            HTTPException: bad request HTTPException when hexadecimal_uuid is not valid UUID string

        Returns:
            UUID: UUID
        """
        try:
            return UUID(hex=hexadecimal_uuid)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid UUID {hexadecimal_uuid}"
            )
