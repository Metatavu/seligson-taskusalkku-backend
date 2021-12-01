# coding: utf-8

import logging
import uuid
import database.operations as database

from typing import List, Optional
from fastapi import HTTPException
from fastapi_utils.cbv import cbv
from spec.apis.funds_api import FundsApiSpec, router as funds_api_router
from datetime import date

from spec.models.fund import Fund
from spec.models.historical_value import HistoricalValue
from spec.models.extra_models import TokenModel
from funds.funds_meta import FundsMetaController
from funds.funds_meta import FundMeta
from spec.models.localized_value import LocalizedValue
from spec.models.change_data import ChangeData

from database.models import Fund as DbFund
from database.models import FundRate

logger = logging.getLogger(__name__)


@cbv(funds_api_router)
class FundsApiImpl(FundsApiSpec):

    fundsMetaController: FundsMetaController = FundsMetaController()

    async def find_fund(self,
                        fund_id: uuid,
                        token_bearer: TokenModel
                        ) -> Fund:

        fund = database.find_fund(
            database=self.database,
            id=fund_id
        )

        if not fund:
            raise HTTPException(
                                status_code=404,
                                detail="Fund {fund_id} not found"
                              )

        return self.translate_fund(fund=fund)

    async def list_funds(self,
                         first_result: int,
                         max_results: int,
                         token_bearer: TokenModel
                         ) -> List[Fund]:

        if not first_result:
            first_result = 0

        if not max_results:
            max_results = 10

        if first_result < 0:
            raise HTTPException(
                                 status_code=400,
                                 detail="Invalid first result parameter cannot be negative"
                               )

        if max_results < 0:
            raise HTTPException(
                                 status_code=400,
                                 detail="Invalid max results parameter cannot be negative"
                               )

        funds = database.list_funds(
          database=self.database,
          first_result=first_result,
          max_result=max_results
        )

        return list(map(self.translate_fund, funds))

    async def list_historical_values(self,
                                     fund_id: str,
                                     first_result: int,
                                     max_results: int,
                                     start_date: date,
                                     end_date: date,
                                     token_bearer: TokenModel
                                     ) -> List[HistoricalValue]:

        fund = database.find_fund(
            database=self.database,
            id=fund_id
        )

        if not fund:
            raise HTTPException(
                                status_code=404,
                                detail="Fund {fund_id} not found"
                               )

        values = database.query_fund_rates(
            database=self.database,
            fund_id=fund.id,
            rate_date_min=start_date,
            rate_date_max=end_date,
            first_result=first_result,
            max_result=max_results
        )

        return list(map(self.translate_historical_value, values))

    def translate_fund(self, fund: DbFund) -> Fund:
        """Translates fund to REST resource

        Args:
            fund_meta (FundMeta): fund meta entry

        Returns:
            Fund: Translated REST resource
        """

        fund_meta = self.fundsMetaController.get_fund_meta_by_fund_code(fund_code=fund.security_id)
        if fund_meta is None:
            raise HTTPException(
                                status_code=404,
                                detail="Fund meta for fund {fund_id} not found"
                              )

        name = LocalizedValue(
            fi=fund.security_name_fi,
            sv=fund.security_name_sv
        )

        long_name = self.translate_meta_locale(fund_meta["long_name"])
        short_name = self.translate_meta_locale(fund_meta["short_name"])

        kiid = self.translate_meta_locale(fund_meta.get("kiid",  None))
        result = Fund(
                      id=str(fund.id),
                      name=name,
                      longName=long_name,
                      shortName=short_name,
                      KIID=kiid,
                      color=fund_meta["color"],
                      risk=fund_meta["risk"],
                      bankReceiverName=fund_meta.get("subs_name", None),
                      group=fund_meta["group"],
                      priceDate=fund_meta["price_date"],
                      aShareValue=fund_meta["a_share_value"],
                      bShareValue=fund_meta["b_share_value"],
                      changeData=self.translate_change_date(fund_meta),
                      profitProjection=fund_meta["profit_projection"],
                      profitProjectionDate=fund_meta["profit_projection_date"]
                  )

        return result

    def translate_change_date(self, fund_meta: FundMeta) -> ChangeData:
        """Translates change data from fund meta object

        Args:
            fund_meta (FundMeta): fund meta object

        Returns:
            ChangeData: change data
        """
        return ChangeData(
            change1d=fund_meta["_1d_change"],
            change1m=fund_meta["_1m_change"],
            change1y=fund_meta["_1y_change"],
            change3y=fund_meta["_3y_change"],
            change5y=fund_meta["_5y_change"],
            change10y=fund_meta["_10y_change"],
            change15y=fund_meta["_15y_change"],
            change20y=fund_meta["_20y_change"],
        )

    def translate_meta_locale(self,
                              meta_locale: Optional[List[str]]
                              ) -> Optional[LocalizedValue]:
        """Translates localized value from fund meta to LocalizedValue

        Args:
            meta_locale (List[str]): [description]

        Returns:
            LocalizedValue: [description]
        """
        if not meta_locale:
            return None

        fi = meta_locale[0] if len(meta_locale) > 0 else None
        sv = meta_locale[1] if len(meta_locale) > 1 else None

        return LocalizedValue(
            fi=fi,
            sv=sv
        )

    def translate_historical_value(self, fund_rate: FundRate) -> HistoricalValue:
        """Translates historical value

        Args:
            rate_rah (RATErah): single row from RATErah table

        Returns:
            HistoricalValue: REST resource
        """
        result = HistoricalValue()
        result.value = fund_rate.rate_close
        result.date = fund_rate.rate_date
        return result
