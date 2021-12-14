# coding: utf-8

import logging
from uuid import UUID
from database import operations

from typing import List, Optional
from fastapi import HTTPException
from fastapi_utils.cbv import cbv
from spec.apis.securities_api import SecuritiesApiSpec, router as securities_api_router

from spec.models.security import Security, LocalizedValue
from spec.models.extra_models import TokenModel

from database.models import Security as DbSecurity

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
            max_result=max_results
        )

        return list(map(self.translate_security, securities))

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