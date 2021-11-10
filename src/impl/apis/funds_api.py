# coding: utf-8

from typing import List, Optional, Union
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

logger = logging.getLogger(__name__)


@cbv(FundsApiRouter)
class FundsApiImpl(FundsApiSpec):

    fundsMetaController: FundsMetaController = FundsMetaController()

    async def find_fund(self,
                        fund_id: uuid,
                        token_bearerAuth: TokenModel
                        ) -> Fund:
        fund_meta = self.fundsMetaController.get_fund_meta_by_fund_id(fund_id = fund_id)
        if not fund_meta:
          raise HTTPException(status_code=404, detail="Fund {fund_id} not found")

        return self.translate_fund(fund_meta = fund_meta)

         
        
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
                      long_name=long_name,
                      short_name=short_name,
                      kiid=kiid,
                      color=fund_meta["color"],
                      risk=fund_meta["risk"],
                      bank_receiver_name=None,
                      group=fund_meta["group"],
                      price_date=None,
                      a_share_value=None,
                      b_share_value=None,
                      change_data=None,
                      profit_projection=None,
                      profit_projection_date=None
                  )
                
        return result

    def translate_meta_locale(self, meta_locale: Optional[List[str]]) -> Optional[LocalizedValue]:
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
            fi = fi,
            sv = sv
        )
