# coding: utf-8
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
from business_logics import business_logics
from database.models import PortfolioTransaction,Company
from spec.models.portfolio_fund import PortfolioFund
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
        """
        find a portfolio
        """
        user_ssn = self.get_user_ssn(token_bearer)
        portfolio = Portfolio()
        if user_ssn:
            valid_company_codes = self.get_valid_company_codes(user_ssn)
            company_code = operations.get_company_code_of_portfolio(self.database, valid_company_codes, portfolio_id)
            if company_code:
                portfolio_query_result = operations.find_portfolio(self.database, company_code)
                if portfolio_query_result:
                    portfolio = self.portfolios_deserializer(portfolio_query_result[0])
        return portfolio

    async def get_portfolio_summary(
            self,
            portfolio_id: uuid,
            start_date: date,
            end_date: date,
            token_bearer: TokenModel
    ) -> PortfolioSummary:
        """ get portfolio history summary
        """

        transaction_codes = business_logics.get_transaction_codes_for_subscription_redemption()
        portfolio_original_id = operations.get_portfolio_id_from_portfolio_uuid(self.database, portfolio_id)
        query_result = operations.get_portfolio_summary(self.database, portfolio_original_id, start_date,
                                                        end_date,
                                                        transaction_codes)

        redemptions = 0
        subscriptions = 0
        for result in query_result:
            if business_logics.transaction_is_subscription(result.transaction_code):
                subscriptions += result.c_total_value
            else:
                redemptions += result.c_total_value

        result = PortfolioSummary(subscriptions=subscriptions,
                                  redemptions=redemptions)

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
        """ list portfolios
        """

        user_ssn = self.get_user_ssn(token_bearer)
        portfolios: List[Portfolio] = []
        if user_ssn:
            valid_company_codes = self.get_valid_company_codes(user_ssn)
            for com_code in valid_company_codes:
                values = operations.find_portfolio(self.database, com_code)
                if values:
                    portfolio = list(map(self.portfolios_deserializer, values))
                    portfolios.extend(portfolio)
        return portfolios

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

    async def list_portfolio_funds(
        self,
        portfolio_id: uuid,
        token_bearer: TokenModel
    ) -> List[PortfolioFund]:
        raise NotImplementedError

    def portfolios_deserializer(self, values) -> Portfolio:
        """
        desrialize input and creates portfolio
        """
        result = Portfolio()
        result.id = str(operations.get_portfolio_uuid_from_portfolio_id(self.database, values.id))
        result.totalAmount = float(values.totalAmount)
        result.marketValueTotal = float(values.marketValueTotal)
        result.purchaseTotal = float(values.purchaseTotal)
        return result

    @staticmethod
    def com_code_deserializer(company: Company) -> str:
        """
        deserialize input to get com_code
        """
        return company.company_code
