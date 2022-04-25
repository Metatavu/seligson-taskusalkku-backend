# coding: utf-8
import logging
from uuid import UUID

from auth.auth_utils import AuthUtils
from fastapi import HTTPException
from fastapi_utils.cbv import cbv
from spec.apis.companies_api import CompaniesApiSpec, router as companies_api_router
from spec.models.extra_models import TokenModel
from spec.models.company import Company
from database import operations
from database.models import Company as DbCompany

logger = logging.getLogger(__name__)


@cbv(companies_api_router)
class CompaniesApiImpl(CompaniesApiSpec):

    async def find_company(
            self,
            company_id: UUID,
            token_bearer: TokenModel
    ) -> Company:
        ssn = AuthUtils.get_user_ssn(token_bearer=token_bearer)
        if not ssn:
            raise HTTPException(
                status_code=403,
                detail=f"Cannot resolve logged user SSN"
            )

        company = operations.find_company(
            database=self.database,
            company_id=company_id
        )

        if not company:
            raise HTTPException(
                status_code=404,
                detail=f"Company with id {company_id} not found"
            )

        owned = company.ssn == ssn
        if not owned:
            company_access = operations.find_company_access_by_ssn_and_company_id(
                database=self.database,
                ssn=ssn,
                company_id=company_id
            )

            if not company_access:
                raise HTTPException(
                    status_code=403,
                    detail=f"No permission to find this company"
                )

        return self.translate_company(
            company=company,
            owned=owned
        )

    @staticmethod
    def translate_company(company: DbCompany,
                          owned: bool
                          ) -> Company:
        """
        Translates company into REST resource

        Args:
            company: company to translate
            owned: whether the company is owned by the user

        Returns:
            translated company
        """
        access_level = "OWNED" if owned else "SHARED"

        return Company(
            id=str(company.id),
            name=company.name,
            accessLevel=access_level
        )
