# coding: utf-8

from typing import List, Optional
import logging
import uuid

from fastapi import HTTPException
from fastapi_utils.cbv import cbv
from spec.apis.funds_api import FundsApiSpec, router as FundsApiRouter

from spec.models.fund import Fund
from spec.models.historical_value import HistoricalValue
from spec.models.extra_models import TokenModel
from funds.funds_meta import FundsMetaController
from funds.funds_meta import FundMeta
from spec.models.localized_value import LocalizedValue
from src.spec.models.change_data import ChangeData

logger = logging.getLogger(__name__)


@cbv(FundsApiRouter)
class FundsApiImpl(FundsApiSpec):

    fundsMetaController: FundsMetaController = FundsMetaController()

    async def find_fund(self,
                        fund_id: uuid,
                        token_bearerAuth: TokenModel
                        ) -> Fund:
        fund_meta = self.fundsMetaController.get_fund_meta_by_fund_id(fund_id)
        if not fund_meta:
            raise HTTPException(
                                status_code=404,
                                detail="Fund {fund_id} not found"
                              )

        return self.translate_fund(fund_meta=fund_meta)

    async def list_funds(self,
                         first_result: int,
                         max_results: int,
                         token_bearerAuth: TokenModel
                         ) -> List[Fund]:
        fund_metas = self.fundsMetaController.get_all_fund_metas()
        return list(map(self.translate_fund, fund_metas))

    async def list_historical_values(self,
                                     fund_id: str,
                                     first_result: int,
                                     max_results: int,
                                     start_date: str,
                                     end_date: str,
                                     token_bearerAuth: TokenModel
                                     ) -> List[HistoricalValue]:
        ...

    def translate_fund(self, fund_meta: FundMeta) -> Fund:
        """Translates fund to REST resource

        Args:
            fund_meta (FundMeta): fund meta entry

        Returns:
            Fund: Translated REST resource
        """
        long_name = self.translate_meta_locale(fund_meta["long_name"])
        short_name = self.translate_meta_locale(fund_meta["short_name"])
        kiid = self.translate_meta_locale(fund_meta.get("kiid",  None))
        result = Fund(
                      id=str(fund_meta["id"]),
                      name=self.translate_meta_locale(fund_meta["name"]),
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
