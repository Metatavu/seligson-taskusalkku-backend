# coding: utf-8

from typing import List
from fastapi_utils.cbv import cbv
from spec.apis.funds_api import FundsApiSpec, router as FundsApiRouter

from spec.models.fund import Fund
from spec.models.historical_value import HistoricalValue


@cbv(FundsApiRouter)
class FundsApiImpl(FundsApiSpec):

    async def find_fund(self,
                        fund_id: str
                        ) -> Fund:
        ...

    async def list_funds(self,
                         first_result: int,
                         max_results: int
                         ) -> List[Fund]:
        ...

    async def list_historical_values(self,
                                     fund_id: str,
                                     first_result: int,
                                     max_results: int,
                                     start_date: str,
                                     end_date: str
                                     ) -> List[HistoricalValue]:
        ...

