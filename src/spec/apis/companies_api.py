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
from spec.models.company import Company
from spec.models.error import Error
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
class CompaniesApiSpec(ABC):

    database: Session = Depends(get_database)
    settings: Settings = Depends(get_settings)

    @abstractmethod
    async def find_company(
        self,
        company_id: UUID,
        token_bearer: TokenModel,
    ) -> Company:
        ...

    @router.get(
        "/v1/companies/{companyId}",
        responses={
            200: {"model": Company, "description": "Company"},
            400: {"model": Error, "description": "Invalid request was sent to the server"},
            403: {"model": Error, "description": "Attempted to make a call with unauthorized client"},
            500: {"model": Error, "description": "Internal server error"},
        },
        tags=["Companies"],
        summary="Find a company.",
    )
    async def find_company_spec(
        self,
        company_id: str = Path(None, description="company id", alias="companyId"),
        token_bearer: TokenModel = FastAPISecurity(
            get_token_bearer
        ),
    ) -> Company:
        """Finds a company by id."""

        if company_id is None:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter companyId"
            )

        return await self.find_company(
            company_id=self.to_uuid(company_id),
            token_bearer=token_bearer
        )

    @abstractmethod
    async def list_companies(
        self,
        token_bearer: TokenModel,
    ) -> List[Company]:
        ...

    @router.get(
        "/v1/companies",
        responses={
            200: {"model": List[Company], "description": "Companies"},
            400: {"model": Error, "description": "Invalid request was sent to the server"},
            403: {"model": Error, "description": "Attempted to make a call with unauthorized client"},
            500: {"model": Error, "description": "Internal server error"},
        },
        tags=["Companies"],
        summary="Lists companies",
    )
    async def list_companies_spec(
        self,
        token_bearer: TokenModel = FastAPISecurity(
            get_token_bearer
        ),
    ) -> List[Company]:
        """Lists companies"""

        return await self.list_companies(
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
