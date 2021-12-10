# coding: utf-8
import logging
import uuid

from functools import reduce
from typing import List
from fastapi import HTTPException
from fastapi_utils.cbv import cbv
from spec.apis.portfolios_api import PortfoliosApiSpec, router as portfolios_api_router
from datetime import date
from spec.models.extra_models import TokenModel
from spec.models.portfolio import Portfolio
from admin.keycloak_admin import KeycloakAdminAccess
from spec.models.portfolio_summary import PortfolioSummary
from spec.models.portfolio_history_value import PortfolioHistoryValue
from database import operations
from business_logics import business_logics
from database.models import PortfolioTransaction, Company, Portfolio as DbPortfolio
from spec.models.portfolio_security import PortfolioSecurity
from spec.models.transaction_type import TransactionType

logger = logging.getLogger(__name__)


@cbv(portfolios_api_router)
class PortfoliosApiImpl(PortfoliosApiSpec):

    @staticmethod
    def get_user_ssn(token_bearer: TokenModel) -> str:
        """
        get user ssn from keycloak admin
        """
        keycloak_admin_access = KeycloakAdminAccess()
        return keycloak_admin_access.get_user_ssn(token_bearer.get("sub", ""))

    def get_valid_company_codes(self, user_ssn: str) -> [str]:
        valid_company_codes_result = operations.get_companies(self.database, user_ssn)
        return list(map(self.com_code_deserializer, valid_company_codes_result))

    async def find_portfolio(
            self,
            portfolio_id: uuid,
            token_bearer: TokenModel
    ) -> Portfolio:
        portfolio = operations.find_portfolio(
            database=self.database,
            portfolio_id=portfolio_id
        )

        if not portfolio:
            raise HTTPException(
                                status_code=404,
                                detail=f"Portfolio {portfolio_id} not found"
                              )

        ssn = self.get_user_ssn(token_bearer=token_bearer)
        if not ssn:
            raise HTTPException(
                status_code=401,
                detail=f"Cannot resolve logged user SSN"
            )

        if portfolio.company.ssn != ssn:
            raise HTTPException(
                status_code=403,
                detail=f"No permission to find this portfolio"
            )

        return self.translate_portfolio(
            portfolio=portfolio
        )

    async def get_portfolio_summary(
            self,
            portfolio_id: uuid,
            start_date: date,
            end_date: date,
            token_bearer: TokenModel
    ) -> PortfolioSummary:
        """ get portfolio history summary"""

        portfolio = operations.find_portfolio(
            database=self.database,
            portfolio_id=portfolio_id
        )

        if not portfolio:
            raise HTTPException(
                status_code=404,
                detail=f"Portfolio {portfolio_id} not found"
            )

        ssn = self.get_user_ssn(token_bearer=token_bearer)
        if not ssn:
            raise HTTPException(
                status_code=401,
                detail=f"Cannot resolve logged user SSN"
            )

        if portfolio.company.ssn != ssn:
            raise HTTPException(
                status_code=403,
                detail=f"No permission to find this portfolio"
            )

        transaction_codes = business_logics.get_transaction_codes_for_subscription_redemption()

        summary = operations.get_portfolio_summary(
            database=self.database,
            portfolio=portfolio,
            start_date=start_date,
            end_date=end_date,
            transaction_codes=transaction_codes
        )

        redemptions = 0
        subscriptions = 0

        for result in summary:
            if business_logics.transaction_is_subscription(result.transaction_code):
                subscriptions += result.c_total_value
            else:
                redemptions += result.c_total_value

        result = PortfolioSummary(subscriptions=subscriptions,redemptions=redemptions)

        return result

    async def list_portfolio_history_values(
            self,
            portfolio_id: uuid,
            start_date: date,
            end_date: date,
            token_bearer: TokenModel
    ) -> List[PortfolioHistoryValue]:
        raise NotImplementedError

    async def list_portfolios(
            self,
            token_bearer: TokenModel,
    ) -> List[Portfolio]:
        """ list portfolios"""

        ssn = self.get_user_ssn(token_bearer=token_bearer)
        if not ssn:
            raise HTTPException(
                status_code=401,
                detail=f"Cannot resolve logged user SSN"
            )

        companies = operations.get_companies(
            database=self.database,
            ssn=ssn
        )

        portfolios = []

        for company in companies:
            portfolios = portfolios + company.portfolios

        return list(map(self.translate_portfolio, portfolios))

    async def list_portfolio_transactions(
        self,
        portfolio_id: uuid,
        start_date: date,
        end_date: date,
        transaction_type: TransactionType,
        token_bearer: TokenModel
    ) -> List[PortfolioTransaction]:
        raise NotImplementedError

    async def find_portfolio_transactions(
        self,
        portfolio_id: uuid,
        transaction_id: uuid,
        token_bearer: TokenModel
    ) -> PortfolioTransaction:
        raise NotImplementedError

    async def list_portfolio_securities(
        self,
        portfolio_id: uuid,
        token_bearer: TokenModel
    ) -> List[PortfolioSecurity]:
        portfolio = operations.find_portfolio(
            database=self.database,
            portfolio_id=portfolio_id
        )

        if not portfolio:
            raise HTTPException(
                                status_code=404,
                                detail=f"Portfolio {portfolio_id} not found"
                              )

        ssn = self.get_user_ssn(token_bearer=token_bearer)
        if not ssn:
            raise HTTPException(
                status_code=401,
                detail=f"Cannot resolve logged user SSN"
            )

        if portfolio.company.ssn != ssn:
            raise HTTPException(
                status_code=403,
                detail=f"No permission to find this portfolio"
            )

        portfolio_securities = operations.get_portfolio_security_values(
            database=self.database,
            portfolio=portfolio
        )

        return list(map(self.translate_portfolio_security, portfolio_securities))

    def translate_portfolio(self, portfolio: DbPortfolio) -> Portfolio:
        """
        Translates portfolio into REST resource
        """
        portfolio_values = operations.find_portfolio_values(
            database=self.database,
            portfolio=portfolio
        )

        result = Portfolio()
        result.id = str(portfolio.id)
        result.totalAmount = portfolio_values.totalAmount if portfolio_values.totalAmount is not None else "0"
        result.marketValueTotal = portfolio_values.marketValueTotal if portfolio_values.marketValueTotal is not None \
            else "0"
        result.purchaseTotal = portfolio_values.purchaseTotal if portfolio_values.purchaseTotal is not None else "0"

        return result

    @staticmethod
    def translate_portfolio_security(portfolio_security_values: operations.PortfolioSecurityValues) -> Portfolio:
        """
        Translates portfolio security into REST resource
        """
        return PortfolioSecurity(
            id=str(portfolio_security_values.security_id),
            amount=str(portfolio_security_values.totalAmount),
            totalValue=str(portfolio_security_values.marketValueTotal),
            purchaseValue=str(portfolio_security_values.purchaseTotal)
        )

    @staticmethod
    def com_code_deserializer(company: Company) -> str:
        """
        deserialize input to get com_code
        """
        return company.original_id
