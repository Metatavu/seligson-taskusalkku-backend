# coding: utf-8

from typing import List
import logging

from fastapi import FastAPI
from fastapi_utils.cbv import cbv
from spec.apis.funds_api import FundsApiSpec, router as FundsApiRouter

from spec.models.fund import Fund

from spec.models.historical_value import HistoricalValue
from spec.models.extra_models import TokenModel

from db.database import SessionLocal
from db import db_operations, sqlalchemy_models
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@cbv(FundsApiRouter)
class FundsApiImpl(FundsApiSpec):

    async def find_fund(self,
                        fund_id: str,
                        token_bearerAuth: TokenModel,
                        db: Session = None,
                        ) -> Fund:

        ...

    async def list_funds(self,
                         first_result: int,
                         max_results: int,
                         token_bearerAuth: TokenModel,
                         db: Session = None,
                         ) -> List[Fund]:
        ...

    async def list_historical_values(self,
                                     fund_id: str,
                                     first_result: int,
                                     max_results: int,
                                     start_date: str,
                                     end_date: str,
                                     token_bearerAuth: TokenModel,
                                     db: Session = None,
                                     ) -> List[HistoricalValue]:
        ...

