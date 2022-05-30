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
from config.settings import Settings

from spec.models.extra_models import TokenModel  # noqa: F401
from spec.models.error import Error
from spec.models.portfolio import Portfolio
from spec.models.portfolio_history_value import PortfolioHistoryValue
from spec.models.portfolio_security import PortfolioSecurity
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
    database_uri = os.environ["BACKEND_DATABASE_URL"]
    return FastAPISessionMaker(database_uri)


@lru_cache()
def get_settings():
    return Settings()


@cbv(router)
class PortfoliosApiSpec(ABC):

    database: Session = Depends(get_database)
    settings: Settings = Depends(get_settings)

    @abstractmethod
    async def find_portfolio(
        self,
        portfolio_id: UUID,
        token_bearer: TokenModel,
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
        portfolio_id: str = Path(None, description="portfolio id", alias="portfolioId"),
        token_bearer: TokenModel = FastAPISecurity(
            get_token_bearer
        ),
    ) -> Portfolio:
        """Finds a portfolio by id."""

        if portfolio_id is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter portfolioId"
            )

        return await self.find_portfolio(
            portfolio_id=self.to_uuid(portfolio_id),
            token_bearer=token_bearer
        )

    @abstractmethod
    async def find_portfolio_transaction(
        self,
        portfolio_id: UUID,
        transaction_id: UUID,
        token_bearer: TokenModel,
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
        summary="Finds portfolio transaction",
    )
    async def find_portfolio_transaction_spec(
        self,
        portfolio_id: str = Path(None, description="Portfolio id", alias="portfolioId"),
        transaction_id: str = Path(None, description="Transaction id", alias="transactionId"),
        token_bearer: TokenModel = FastAPISecurity(
            get_token_bearer
        ),
    ) -> PortfolioTransaction:
        """Returns found portfolio transaction"""

        if portfolio_id is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter portfolioId"
            )

        if transaction_id is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter transactionId"
            )

        return await self.find_portfolio_transaction(
            portfolio_id=self.to_uuid(portfolio_id),
            transaction_id=self.to_uuid(transaction_id),
            token_bearer=token_bearer
        )

    @abstractmethod
    async def get_portfolio_summary(
        self,
        portfolio_id: UUID,
        start_date: date,
        end_date: date,
        token_bearer: TokenModel,
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
    async def get_portfolio_summary_spec(
        self,
        portfolio_id: str = Path(None, description="portfolio id", alias="portfolioId"),
        start_date: str = Query(None, description="Start date for the date range", alias="startDate"),
        end_date: str = Query(None, description="End date for the date range", alias="endDate"),
        token_bearer: TokenModel = FastAPISecurity(
            get_token_bearer
        ),
    ) -> PortfolioSummary:
        """Returns summary a portfolio history for given time range"""

        if portfolio_id is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter portfolioId"
            )

        if start_date is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter startDate"
            )

        if end_date is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter endDate"
            )

        return await self.get_portfolio_summary(
            portfolio_id=self.to_uuid(portfolio_id),
            start_date=self.to_date(start_date),
            end_date=self.to_date(end_date),
            token_bearer=token_bearer
        )

    @abstractmethod
    async def list_portfolio_history_values(
        self,
        portfolio_id: UUID,
        start_date: date,
        end_date: date,
        token_bearer: TokenModel,
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
        portfolio_id: str = Path(None, description="portfolio id", alias="portfolioId"),
        start_date: str = Query(None, description="Start date for the date range", alias="startDate"),
        end_date: str = Query(None, description="End date for the date range", alias="endDate"),
        token_bearer: TokenModel = FastAPISecurity(
            get_token_bearer
        ),
    ) -> List[PortfolioHistoryValue]:
        """Lists portfolio history values"""

        if portfolio_id is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter portfolioId"
            )

        if start_date is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter startDate"
            )

        if end_date is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter endDate"
            )

        return await self.list_portfolio_history_values(
            portfolio_id=self.to_uuid(portfolio_id),
            start_date=self.to_date(start_date),
            end_date=self.to_date(end_date),
            token_bearer=token_bearer
        )

    @abstractmethod
    async def list_portfolio_securities(
        self,
        portfolio_id: UUID,
        token_bearer: TokenModel,
    ) -> List[PortfolioSecurity]:
        ...

    @router.get(
        "/v1/portfolios/{portfolioId}/securities",
        responses={
            200: {"model": List[PortfolioSecurity], "description": "List of portfolio securities"},
            400: {"model": Error, "description": "Invalid request was sent to the server"},
            403: {"model": Error, "description": "Attempted to make a call with unauthorized client"},
            404: {"model": Error, "description": "Not found"},
            500: {"model": Error, "description": "Internal server error"},
        },
        tags=["Portfolios"],
        summary="Lists portfolio funds",
    )
    async def list_portfolio_securities_spec(
        self,
        portfolio_id: str = Path(None, description="portfolio id", alias="portfolioId"),
        token_bearer: TokenModel = FastAPISecurity(
            get_token_bearer
        ),
    ) -> List[PortfolioSecurity]:
        """Returns list of portfolio funds"""

        if portfolio_id is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter portfolioId"
            )

        return await self.list_portfolio_securities(
            portfolio_id=self.to_uuid(portfolio_id),
            token_bearer=token_bearer
        )

    @abstractmethod
    async def list_portfolio_transactions(
        self,
        portfolio_id: UUID,
        start_date: Optional[date],
        end_date: Optional[date],
        transaction_type: Optional[TransactionType],
        token_bearer: TokenModel,
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
        portfolio_id: str = Path(None, description="portfolio id", alias="portfolioId"),
        start_date: str = Query(None, description="Start date for the date range", alias="startDate"),
        end_date: str = Query(None, description="End date for the date range", alias="endDate"),
        transaction_type: TransactionType = Query(None, description="Transaction type", alias="transactionType"),
        token_bearer: TokenModel = FastAPISecurity(
            get_token_bearer
        ),
    ) -> List[PortfolioTransaction]:
        """Returns list of portfolio transactions"""

        if portfolio_id is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter portfolioId"
            )

        return await self.list_portfolio_transactions(
            portfolio_id=self.to_uuid(portfolio_id),
            start_date=self.to_date(start_date),
            end_date=self.to_date(end_date),
            transaction_type=transaction_type,
            token_bearer=token_bearer
        )

    @abstractmethod
    async def list_portfolios(
        self,
        company_id: Optional[UUID],
        token_bearer: TokenModel,
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
        company_id: str = Query(None, description="company id", alias="companyId"),
        token_bearer: TokenModel = FastAPISecurity(
            get_token_bearer
        ),
    ) -> List[Portfolio]:
        """Lists portfolios logged user has access to"""

        return await self.list_portfolios(
            company_id=self.to_uuid(company_id),
            token_bearer=token_bearer
        )

    @abstractmethod
    async def list_portfolios_v2(
        self,
        company_id: Optional[UUID],
        token_bearer: TokenModel,
    ) -> List[Portfolio]:
        ...

    @router.get(
        "/v2/portfolios",
        responses={
            200: {"model": List[Portfolio], "description": "List of portfolios"},
            400: {"model": Error, "description": "Invalid request was sent to the server"},
            403: {"model": Error, "description": "Attempted to make a call with unauthorized client"},
            500: {"model": Error, "description": "Internal server error"},
        },
        tags=["Portfolios"],
        summary="List portfolios.",
    )
    async def list_portfolios_v2_spec(
        self,
        company_id: str = Query(None, description="company id", alias="companyId"),
        token_bearer: TokenModel = FastAPISecurity(
            get_token_bearer
        ),
    ) -> List[Portfolio]:
        """Lists portfolios logged user has access to"""

        return await self.list_portfolios_v2(
            company_id=self.to_uuid(company_id),
            token_bearer=token_bearer
        )

    @staticmethod
    def to_date(isodate: str) -> Optional[date]:
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

    @staticmethod
    def to_uuid(hexadecimal_uuid: str) -> Optional[UUID]:
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
