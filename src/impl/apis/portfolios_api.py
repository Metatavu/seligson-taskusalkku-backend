# coding: utf-8
import decimal
import logging
import uuid

from typing import List
from fastapi_utils.cbv import cbv
from spec.apis.portfolios_api import PortfoliosApiSpec, router as portfolios_api_router
from datetime import date
from spec.models.extra_models import TokenModel
from spec.models.portfolio import Portfolio
from admin.keycloak_admin import KeycloakAdminAccess
from spec.models.portfolio_summary import PortfolioSummary
from spec.models.portfolio_history_value import PortfolioHistoryValue
from database import operations
from database.sqlalchemy_models import COMPANYrah
from business_logics import business_logics

logger = logging.getLogger(__name__)


@cbv(portfolios_api_router)
class PortfoliosApiImpl(PortfoliosApiSpec):

    @staticmethod
    def get_user_ssn(token_bearer: TokenModel) -> str:
        """
        get user ssn from keycloak admin
        """
        keycloak_admin_access = KeycloakAdminAccess()
        return keycloak_admin_access.get_user_id(token_bearer.get("sub", ""))

    def get_valid_company_codes(self, user_id: str) -> [str]:
        valid_company_codes_result = operations.get_company(self.database, user_id)
        return list(map(self.com_code_deserializer, valid_company_codes_result))

    async def find_portfolio(
            self,
            portfolio_id: uuid,
            token_bearer: TokenModel
    ) -> Portfolio:
        """
        find a portfolio
        """
        user_id = self.get_user_id(token_bearer)
        portfolio = Portfolio()
        if user_id:
            valid_company_codes = self.get_valid_company_codes(user_id)
            company_code = operations.get_company_code_of_portfolio(self.database, valid_company_codes, portfolio_id)
            if company_code:
                portfolio_query_result = operations.find_portfolio(self.database, company_code)
                if portfolio_query_result:
                    portfolio = self.portfolios_deserializer(portfolio_query_result[0])
        return portfolio

    async def get_portfolio_h_summary(
            self,
            portfolio_id: uuid,
            start_date: date,
            end_date: date,
            token_bearer: TokenModel
    ) -> PortfolioSummary:
        """ get portfolio history summary
        """

        transaction_codes = business_logics.get_transaction_codes_for_subscription_redemption()
        query_result = operations.get_portfolio_summary(self.database, portfolio_id, start_date,
                                                        end_date,
                                                        transaction_codes)
        redemptions = decimal.Decimal("0")
        subscriptions = decimal.Decimal("0")
        for result in query_result:
            if business_logics.transaction_is_subscription(result.TRANS_CODE):
                subscriptions += result.CTOT_VALUE * 100
            else:
                redemptions += result.CTOT_VALUE * 100

        result = PortfolioSummary(subscriptions=subscriptions,
                                  redemptions=redemptions)

        return result

    async def list_portfolio_history_values(
            self,
            portfolioId: uuid,
            start_date: date,
            end_date: date,
            token_bearer: TokenModel
    ) -> List[PortfolioHistoryValue]:
        pass

    async def list_portfolios(
            self,
            token_bearer: TokenModel,
    ) -> List[Portfolio]:
        """ list portfolios
        """

        user_id = self.get_user_id(token_bearer)
        portfolios: List[Portfolio] = []
        if user_id:
            valid_company_codes = self.get_valid_company_codes(user_id)
            for com_code in valid_company_codes:
                values = operations.get_portfolio(self.database, com_code)

                if values:
                    portfolio = list(map(self.portfolios_deserializer, values))
                    portfolios.extend(portfolio)
        return portfolios

    @staticmethod
    def com_code_deserializer(companyrah: COMPANYrah) -> str:
        """
        deserialize input to get com_code
        """
        com_code = companyrah.COM_CODE
        return com_code

    @staticmethod
    def portfolios_deserializer(values) -> Portfolio:
        """
        desrialize input and creates portfolio
        """
        result = Portfolio()
        result.id = values.id
        result.totalAmount = int(values.totalAmount)
        result.marketValueTotal = int(values.marketValueTotal)
        result.purchaseTotal = int(values.purchaseTotal)

        return result
