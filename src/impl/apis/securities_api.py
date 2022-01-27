# coding: utf-8

import logging
from datetime import date
from uuid import UUID
from database import operations

from typing import List, Optional
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
            series_id=series_id
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

        values = operations.query_security_rates(
            database=self.database,
            security_id=security.id,
            rate_date_min=start_date,
            rate_date_max=end_date,
            first_result=first_result,
            max_result=max_results
        )

        return list(map(self.translate_historical_value, values))

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
                sv=security.name_sv
            ),
            currency=security.currency
        )

    @staticmethod
    def translate_historical_value(security_rate: SecurityRate) -> SecurityHistoryValue:
        """Translates historical value

        Args:
            security_rate (SecurityRate): security rate

        Returns:
            SecurityHistoryValue: REST resource
        """
        result = SecurityHistoryValue()
        result.value = security_rate.rate_close
        result.date = security_rate.rate_date
        return result
