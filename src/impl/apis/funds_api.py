# coding: utf-8

import logging
import database.operations as database

from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException
from fastapi_utils.cbv import cbv
from business_logics import business_logics
from spec.apis.funds_api import FundsApiSpec, router as funds_api_router

from spec.models.fund import Fund
from spec.models.extra_models import TokenModel
from funds.funds_meta import FundsMetaController
from funds.funds_meta import FundMeta
from spec.models.localized_value import LocalizedValue
from spec.models.change_data import ChangeData
from spec.models.subscription_bank_account import SubscriptionBankAccount

from database.models import Fund as DbFund
from utils.fund_utils import FundUtils

logger = logging.getLogger(__name__)


@cbv(funds_api_router)
class FundsApiImpl(FundsApiSpec):
    fundsMetaController: FundsMetaController = FundsMetaController()

    async def find_fund(self,
                        fund_id: UUID,
                        token_bearer: TokenModel
                        ) -> Fund:

        fund = database.find_fund(
            database=self.database,
            fund_id=fund_id
        )

        if not fund:
            raise HTTPException(
                status_code=404,
                detail=f"Fund {fund_id} not found"
            )

        result = self.translate_fund(fund=fund)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Fund {fund_id} not found"
            )

        return result

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
            max_result=max_results,
            deprecated=False
        )

        return list(filter(lambda x: x is not None, map(self.translate_fund, funds)))

    def translate_fund(self, fund: DbFund) -> Optional[Fund]:
        """Translates fund to REST resource

        Args:
            fund (DbFund): fund

        Returns:
            Fund: Translated REST resource
        """

        group = fund.group
        if group is None:
            logger.warning("Fund group for fund id %s not found", fund.original_id)
            return None

        risk_level = None
        if fund.risk_level is not None:
            risk_level = int(fund.risk_level)

        color = "rgb(200, 40, 40)"
        if risk_level is not None:
            color = FundUtils.get_fund_color(fund_group=group, risk_level=risk_level).to_css()

        security = database.find_main_security_for_fund(
            database=self.database,
            fund_id=fund.id
        )

        if security is None:
            logger.warning("Fund security for fund id %s not found", fund.original_id)
            return None

        fund_meta = self.fundsMetaController.get_fund_meta(
            fund_id=str(fund.original_id),
            security_id=security.original_id
        )

        price_date = fund_meta["price_date"]

        if fund_meta is None:
            logger.warning("Fund meta for fund id %s not found", fund.original_id)
            return None

        long_name = LocalizedValue(
            fi=FundUtils.get_fund_long_name_from_security_name(security_name=security.name_fi),
            sv=FundUtils.get_fund_long_name_from_security_name(security_name=security.name_sv),
            en=FundUtils.get_fund_long_name_from_security_name(security_name=security.name_en)
        )

        short_name = LocalizedValue(
            fi=FundUtils.get_fund_short_name_from_security_name(security_name=security.name_fi),
            sv=FundUtils.get_fund_short_name_from_security_name(security_name=security.name_sv),
            en=FundUtils.get_fund_short_name_from_security_name(security_name=security.name_en)
        )

        kiid_urls = None

        if fund.kiid_url_fi:
            kiid_urls = LocalizedValue(
                fi=fund.kiid_url_fi,
                sv=fund.kiid_url_sv,
                en=fund.kiid_url_en
            )

        result = Fund(
            id=str(fund.id),
            longName=long_name,
            shortName=short_name,
            KIID=kiid_urls,
            color=color,
            risk=risk_level,
            group=group,
            priceDate=price_date,
            aShareValue=fund_meta["a_share_value"],
            bShareValue=fund_meta["b_share_value"],
            changeData=self.translate_change_date(fund_meta),
            profitProjection=fund_meta["profit_projection"],
            profitProjectionDate=fund_meta["profit_projection_date"],
            subscriptionBankAccounts=self.translate_subscription_bank_account(fund_meta),
            subscribable=business_logics.fund_is_subscribable(fund_original_id=fund.original_id)
        )

        return result

    @staticmethod
    def translate_change_date(fund_meta: FundMeta) -> ChangeData:
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

    @staticmethod
    def translate_subscription_bank_account(fund_meta: FundMeta) -> Optional[List[SubscriptionBankAccount]]:
        return [
            SubscriptionBankAccount(BankAccountName=fund_meta_entry.get("bank_account_name", None),
                                    IBAN=fund_meta_entry.get("iban", None),
                                    AccountNumberOldFormat=fund_meta_entry.get("account_number_old_format", None),
                                    BIC=fund_meta_entry.get("bic", None),
                                    Currency=fund_meta_entry.get("currency", None))
            for fund_meta_entry in fund_meta["bank_info"]] if fund_meta["bank_info"] else None
