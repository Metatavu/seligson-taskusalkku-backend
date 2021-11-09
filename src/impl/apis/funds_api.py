# coding: utf-8

from typing import List
import logging

from fastapi_utils.cbv import cbv
from spec.apis.funds_api import FundsApiSpec, router as FundsApiRouter

from spec.models.fund import Fund
from spec.models.historical_value import HistoricalValue
from spec.models.extra_models import TokenModel

logger = logging.getLogger(__name__)


@cbv(FundsApiRouter)
class FundsApiImpl(FundsApiSpec):

    async def find_fund(self,
                        fund_id: str,
                        token_bearerAuth: TokenModel
                        ) -> Fund:

        ...
        
    async def list_funds(self,
                         first_result: int,
                         max_results: int,
                         token_bearerAuth: TokenModel
                         ) -> List[Fund]:
        ...

    async def list_historical_values(self,
                                     fund_id: str,
                                     first_result: int,
                                     max_results: int,
                                     start_date: str,
                                     end_date: str,
                                     token_bearerAuth: TokenModel
                                     ) -> List[HistoricalValue]:
        ...

