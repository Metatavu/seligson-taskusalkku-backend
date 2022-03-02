# coding: utf-8

import logging
from datetime import date
from decimal import Decimal
from uuid import UUID
from database import operations

from typing import List, Optional, Dict
from fastapi import HTTPException
from fastapi_utils.cbv import cbv
from spec.apis.securities_api import SecuritiesApiSpec, router as securities_api_router

from spec.models.security import Security, LocalizedValue
from spec.models.extra_models import TokenModel

from database.models import Security as DbSecurity, SecurityRate
from spec.models.security_history_value import SecurityHistoryValue

logger = logging.getLogger(__name__)


@cbv(securities_api_router)
class SecuritiesApiImpl(SecuritiesApiSpec):

    async def find_security(
            self,
            security_id: UUID,
            token_bearer: TokenModel,
    ) -> Security:

        security = operations.find_security(
            database=self.database,
            security_id=security_id
        )

        if not security:
            raise HTTPException(
                status_code=404,
                detail=f"Security {security_id} not found"
            )

        return self.translate_security(security=security)

    async def list_securities(
            self,
            series_id: Optional[int],
            fund_id: Optional[UUID],
            first_result: Optional[int],
            max_results: Optional[int],
            token_bearer: TokenModel,
    ) -> List[Security]:

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

        securities = operations.list_securities_with_fund(
            database=self.database,
            first_result=first_result,
            max_result=max_results,
            series_id=series_id,
            fund_id=fund_id
        )

        return list(map(self.translate_security, securities))

    async def list_security_history_values(self,
                                           security_id: UUID,
                                           first_result: Optional[int],
                                           max_results: Optional[int],
                                           start_date: Optional[date],
                                           end_date: Optional[date],
                                           token_bearer: TokenModel
                                           ) -> List[SecurityHistoryValue]:

        security = operations.find_security(
            database=self.database,
            security_id=security_id
        )

        if not security:
            raise HTTPException(
                status_code=404,
                detail=f"Security {security_id} not found"
            )

        security_values = operations.query_security_rates(
            database=self.database,
            security_id=security.id,
            rate_date_min=start_date,
            rate_date_max=end_date,
            first_result=first_result,
            max_result=max_results
        )
        if security.currency == self.settings.EURO_CURRENCY_CODE:
            results = list(map(self.translate_historical_value, security_values))
        else:
            currency_security = operations.find_security_by_original_id(
                database=self.database,
                original_id=security.currency
            )
            currency_security_values = operations.query_security_rates(
                database=self.database,
                security_id=currency_security.id,
                rate_date_min=start_date,
                rate_date_max=end_date,
                first_result=first_result,
                max_result=max_results
            )
            results = self.get_non_euro_security_history_values(security_values, currency_security_values)
        return results

    def get_non_euro_security_history_values(self, security_rate_values: c,
                                             currency_security_values: List[SecurityRate]) -> List[SecurityHistoryValue]:
        currency_security_rates: Dict[date, Decimal] = {
            currency_security_value.rate_date: currency_security_value.rate_close for currency_security_value in
            currency_security_values}
        security_rates: Dict[date, Decimal] = {security_value.rate_date: security_value.rate_close for security_value in
                                               security_rate_values}
        currency_rate_dates: List[date] = list(currency_security_rates.keys())
        currency_rate_dates.sort()
        results: List[SecurityHistoryValue] = []
        for security_rate_value in security_rate_values:
            security_history_value = SecurityHistoryValue()
            security_rate_date = security_rate_value.rate_date
            currency_rate_date = self.get_closest_date(currency_rate_dates, security_rate_date)
            security_history_value.date = security_rate_date
            security_history_value.value = security_rates[security_rate_date] / currency_security_rates[
                currency_rate_date]
            results.append(security_history_value)

        return results

    @staticmethod
    def get_closest_date(currency_rate_dates: List[date], security_rate_date: date)-> date:
        """get the closest date to a security_rate date, if there is no currency rate for the same date in security_rate
        Args:
            security_rate_date: date of security_rate
            currency_rate_dates: dates of currency security_rate

        Returns:
            date: closest date to the security_rate_date
        """
        return min(currency_rate_dates, key=lambda rate_date: abs(security_rate_date - rate_date))

    @staticmethod
    def translate_security(security: DbSecurity) -> Security:
        """Translates security to REST resource

        Args:
            security (DbSecurity): security

        Returns:
            Security: Translated REST resource
        """

        return Security(
            id=str(security.id),
            fundId=str(security.fund_id),
            name=LocalizedValue(
                fi=security.name_fi,
                sv=security.name_sv,
                en=security.name_en
            ),
            currency=security.currency
        )

    def translate_historical_value(self, security_rate: SecurityRate) -> SecurityHistoryValue:
        """Translates historical value

        Args:
            security_rate (SecurityRate): security rate

        Returns:
            SecurityHistoryValue: REST resource
        """
        result = SecurityHistoryValue()
        last_fim_date = self.settings.LAST_FIM_DATE
        fim_convert_rate = self.settings.FIM_CONVERT_RATE
        result.date = security_rate.rate_date
        result.value = security_rate.rate_close if result.date > last_fim_date else security_rate.rate_close / fim_convert_rate
        return result
