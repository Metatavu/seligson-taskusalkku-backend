# coding: utf-8
import logging
from uuid import UUID

from typing import List, Optional
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
from database.models import Portfolio as DbPortfolio, PortfolioLog as DbPortfolioLog
from spec.models.portfolio_security import PortfolioSecurity
from spec.models.portfolio_transaction import PortfolioTransaction
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

    async def find_portfolio(
            self,
            portfolio_id: UUID,
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
            portfolio_id: UUID,
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

        result = PortfolioSummary(subscriptions=subscriptions, redemptions=redemptions)

        return result

    async def list_portfolio_history_values(
            self,
            portfolio_id: UUID,
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
            portfolio_id: UUID,
            start_date: date,
            end_date: date,
            transaction_type: TransactionType,
            token_bearer: TokenModel
    ) -> List[PortfolioTransaction]:
        transaction_code = self.get_transaction_code_for_transaction_type(transaction_type=transaction_type)
        transaction_codes = ["11", "12", "46"] if transaction_code is None else [transaction_code]

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

        if not start_date:
            start_date = date(1997, 1, 1)

        if not end_date:
            end_date = date.today()

        portfolio_logs = operations.get_portfolio_logs(
            database=self.database,
            portfolio=portfolio,
            transaction_codes=transaction_codes,
            transaction_date_min=start_date,
            transaction_date_max=end_date,
        )

        return list(map(self.translate_portfolio_log, portfolio_logs))

    async def find_portfolio_transaction(
            self,
            portfolio_id: UUID,
            transaction_id: UUID,
            token_bearer: TokenModel
    ) -> PortfolioTransaction:
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

        portfolio_log = operations.find_portfolio_log(
            database=self.database,
            portfolio_log_id=transaction_id
        )

        if portfolio_log is None:
            raise HTTPException(
                status_code=404,
                detail=f"Portfolio log {transaction_id} not found"
            )

        if portfolio_log.portfolio_id != portfolio.id:
            raise HTTPException(
                status_code=404,
                detail=f"Portfolio log {transaction_id} not found"
            )

        return self.translate_portfolio_log(portfolio_log=portfolio_log)

    async def list_portfolio_securities(
            self,
            portfolio_id: UUID,
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
        result.totalAmount = portfolio_values.total_amount if portfolio_values.total_amount is not None else "0"
        result.marketValueTotal = "0" if portfolio_values.market_value_total is None else \
            portfolio_values.market_value_total
        result.purchaseTotal = portfolio_values.purchase_total if portfolio_values.purchase_total is not None else "0"

        return result

    def translate_portfolio_log(self, portfolio_log: DbPortfolioLog) -> PortfolioTransaction:
        target_security_id = None
        if portfolio_log.c_security_id is not None:
            target_security_id = str(portfolio_log.security_id)

        transaction_type = self.get_transaction_type_for_transaction_code(portfolio_log.transaction_code)

        return PortfolioTransaction(
            id=str(portfolio_log.id),
            securityId=str(portfolio_log.security_id),
            targetSecurityId=target_security_id,
            transactionType=transaction_type,
            valueDate=portfolio_log.transaction_date,
            value=portfolio_log.c_value,
            shareAmount=portfolio_log.amount,
            marketValue=portfolio_log.c_price,
            totalValue=portfolio_log.c_total_value,
            paymentDate=portfolio_log.payment_date,
            provision=portfolio_log.provision
        )

    @staticmethod
    def get_transaction_code_for_transaction_type(transaction_type: Optional[TransactionType]) -> Optional[str]:
        if transaction_type is None:
            return None
        elif transaction_type == "SUBSCRIPTION":
            return '11'
        elif transaction_type == "REDEMPTION":
            return '12'
        elif transaction_type == "SECURITY":
            return '46'

        raise HTTPException(
            status_code=400,
            detail=f"Invalid transaction_type {transaction_type}"
        )

    @staticmethod
    def get_transaction_type_for_transaction_code(transaction_code: str) -> TransactionType:
        if transaction_code == "11":
            return "SUBSCRIPTION"
        elif transaction_code == "12":
            return 'REDEMPTION'
        elif transaction_code == "46":
            return 'SECURITY'

        raise HTTPException(
            status_code=500,
            detail=f"Invalid transaction code found {transaction_code}"
        )

    @staticmethod
    def translate_portfolio_security(
            portfolio_security_values: operations.PortfolioSecurityValues) -> PortfolioSecurity:
        """
        Translates portfolio security into REST resource
        """
        return PortfolioSecurity(
            id=str(portfolio_security_values.security_id),
            amount=str(portfolio_security_values.total_amount),
            totalValue=str(portfolio_security_values.market_value_total),
            purchaseValue=str(portfolio_security_values.purchase_total)
        )
