# coding: utf-8
import logging
from decimal import Decimal
from uuid import UUID

from auth.auth_utils import AuthUtils
from typing import List, Optional, Dict
from fastapi import HTTPException
from fastapi_utils.cbv import cbv
from spec.apis.portfolios_api import PortfoliosApiSpec, router as portfolios_api_router
from datetime import date, timedelta
from spec.models.extra_models import TokenModel
from spec.models.portfolio import Portfolio
from spec.models.portfolio_summary import PortfolioSummary
from spec.models.portfolio_history_value import PortfolioHistoryValue
from database import operations
from business_logics import business_logics
from database.models import Portfolio as DbPortfolio, PortfolioLog as DbPortfolioLog, Security as DbSecurity, \
    Company as DbCompany
from spec.models.portfolio_security import PortfolioSecurity
from spec.models.portfolio_transaction import PortfolioTransaction
from spec.models.transaction_type import TransactionType
from holdings.holdings import Holdings
from utils.portfolio_utils import PortfolioUtils, PortfolioSecurityValues

logger = logging.getLogger(__name__)


@cbv(portfolios_api_router)
class PortfoliosApiImpl(PortfoliosApiSpec):

    async def find_portfolio(
            self,
            portfolio_id: UUID,
            token_bearer: TokenModel
    ) -> Portfolio:
        portfolio = self.get_portfolio(token_bearer=token_bearer, portfolio_id=portfolio_id)
        ssn = AuthUtils.get_user_ssn(token_bearer=token_bearer)
        if not ssn:
            raise HTTPException(
                status_code=403,
                detail=f"Cannot resolve logged user SSN"
            )

        own_companies = operations.get_companies(
            database=self.database,
            ssn=ssn
        )

        return self.translate_portfolio(
            portfolio=portfolio,
            own_companies=own_companies
        )

    async def get_portfolio_summary(
            self,
            portfolio_id: UUID,
            start_date: date,
            end_date: date,
            token_bearer: TokenModel
    ) -> PortfolioSummary:
        """ get portfolio history summary"""

        portfolio = self.get_portfolio(token_bearer=token_bearer, portfolio_id=portfolio_id)

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
            elif business_logics.transaction_is_redemption(result.transaction_code):
                redemptions += result.c_total_value

        result = PortfolioSummary(subscriptions=subscriptions, redemptions=redemptions)

        return result

    def get_security_rate_map(self, security_id: UUID, min_date: date, max_date: date) -> Dict[date, Decimal]:
        security_rates = operations.query_security_rates(
            database=self.database,
            security_id=security_id,
            rate_date_min=min_date,
            rate_date_max=max_date
        )

        date_rates: Dict[date, Decimal] = {x.rate_date: x.rate_close for x in security_rates}
        current_date = min_date

        last_rate = operations.find_most_recent_security_rate(
            database=self.database,
            security_id=security_id,
            rate_date_before=min_date
        )

        if last_rate is None:
            raise HTTPException(
                status_code=500,
                detail=f"could not find rate for security {security_id} before {min_date}"
            )

        last_rate_close = last_rate.rate_close

        delta_for_day = timedelta(days=1)

        while current_date <= max_date:
            if current_date not in date_rates:
                date_rates[current_date] = last_rate_close
            else:
                last_rate_close = date_rates[current_date]

            current_date += delta_for_day

        return date_rates

    async def list_portfolio_history_values(
            self,
            portfolio_id: UUID,
            start_date: date,
            end_date: date,
            token_bearer: TokenModel
    ) -> List[PortfolioHistoryValue]:
        portfolio = self.get_portfolio(token_bearer=token_bearer, portfolio_id=portfolio_id)

        if end_date > date.today():
            end_date = date.today()

        """List portfolio transactions from given time period """
        rows: List[DbPortfolioLog] = operations.get_portfolio_logs(
            database=self.database,
            portfolio=portfolio,
            transaction_codes=['11', '31', '46', '80'],
            transaction_date_min=None,
            transaction_date_max=end_date,
        )

        holdings = Holdings()
        securities: Dict[UUID, DbSecurity] = {}
        result: List[PortfolioHistoryValue] = []

        """Add transactions to holdings object"""
        for row in rows:
            transaction_code = row.transaction_code
            is_subscription = transaction_code == "11"
            to_port = transaction_code == "31"
            is_transfer = transaction_code == "46"
            is_removal = transaction_code == "80"

            if is_subscription or to_port:
                """If subscription or a transfer to portfolio, add amount to security position."""
                holdings.add_holding(security_id=row.security_id, amount=row.amount, 
                                     holding_date=row.transaction_date)
            elif is_transfer:
                """If transfer from one security to another, add amount to target security position."""
                holdings.add_holding(security_id=row.c_security_id, amount=row.amount, 
                                     holding_date=row.transaction_date)
            elif is_removal:
                """If any type of removal from portfolio, subtract amount from portfolio position.
                 transaction_code 80 includes redemptions, transfers from one portfolio to another and 
                 transfers from one security to another."""
                holdings.add_holding(security_id=row.security_id, amount=-row.amount,
                                     holding_date=row.transaction_date)

            securities[row.security.id] = row.security

            if row.c_security is not None:
                securities[row.c_security.id] = row.c_security

        """If there are no holdings, the portfolio is empty"""
        if holdings.is_empty():
            return result

        """Resolve if SEK rates if needed"""
        first_sek_date = None
        sek_rates: Dict[date, Decimal] = {}

        for security_id in holdings.get_security_ids():
            security = securities[security_id]
            if "SPILTAN" in security.original_id:
                min_date = holdings.get_security_min_date(security_id=security_id)
                if first_sek_date is None or min_date < first_sek_date:
                    first_sek_date = min_date

        if first_sek_date is not None:
            sek_security = operations.find_security_by_original_id(
                database=self.database,
                original_id="SEK"
            )

            sek_rates = self.get_security_rate_map(
                security_id=sek_security.id,
                min_date=first_sek_date,
                max_date=end_date
            )

        """Resolve EUR rates (including FIM for transactions before 1999-01-01) """
        holdings_min_date = holdings.get_min_date()
        eur_rates: Dict[date, Decimal] = {}
        last_fim_date = self.settings.LAST_FIM_DATE
        fim_convert_rate = self.settings.FIM_CONVERT_RATE

        for i in range((end_date - holdings_min_date).days + 1):
            eur_date = holdings_min_date + timedelta(days=i)
            if eur_date > last_fim_date:
                eur_rates[eur_date] = Decimal(1)
            else:
                eur_rates[eur_date] = fim_convert_rate

        security_rates: Dict[UUID, Dict[date, Decimal]] = {}

        """Resolve rates for all securities"""
        for security_id in holdings.get_security_ids():
            security_rates[security_id] = self.get_security_rate_map(
                security_id=security_id,
                min_date=holdings.get_security_min_date(security_id=security_id),
                max_date=end_date
            )

        """Map correct currency rates to securities"""
        currency_rates: Dict[UUID, Dict[date, Decimal]] = {}

        for security_id in holdings.get_security_ids():
            security = securities[security_id]
            if "SPILTAN" in security.original_id:
                currency_rates[security_id] = sek_rates
            else:
                currency_rates[security_id] = eur_rates

        holdings_min_date = holdings.get_min_date()
        if holdings_min_date > start_date:
            start_date = holdings_min_date

        holdings.calculate_amounts(start_date=start_date, end_date=end_date)

        """Calculate daily sums for all holdings"""
        for i in range((end_date - start_date).days + 1):
            holding_date = start_date + timedelta(days=i)

            day_sum = holdings.get_day_sum(
                holding_date=holding_date,
                currency_rates=currency_rates,
                security_rates=security_rates
            )

            result.append(PortfolioHistoryValue(
                date=holding_date,
                value=day_sum
            ))

        return result

    async def list_portfolios(
            self,
            company_id: Optional[UUID],
            token_bearer: TokenModel,
    ) -> List[Portfolio]:
        """ list portfolios"""
        if not AuthUtils.has_user_role(token_bearer=token_bearer):
            raise HTTPException(
                status_code=403,
                detail="This endpoint is not available for anonymous users"
            )

        ssn = AuthUtils.get_user_ssn(token_bearer=token_bearer)
        if not ssn:
            raise HTTPException(
                status_code=403,
                detail=f"Cannot resolve logged user SSN"
            )

        own_companies = []
        company_access_companies = []

        if company_id:
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

                company_access_companies = [ company ]
            else:
                own_companies = [ company ]
        else:
            own_companies = operations.get_companies(
                database=self.database,
                ssn=ssn
            )

            company_access = operations.get_company_access(
                database=self.database,
                ssn=ssn
            )

            company_access_companies = list(map(lambda i: i.company, company_access))

        companies = own_companies + company_access_companies
        portfolios = []

        for company in companies:
            portfolios = portfolios + company.portfolios

        return list(map(lambda portfolio: self.translate_portfolio(
            portfolio=portfolio,
            own_companies=own_companies
        ), portfolios))

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

        portfolio = self.get_portfolio(token_bearer=token_bearer, portfolio_id=portfolio_id)

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
        portfolio = self.get_portfolio(token_bearer=token_bearer, portfolio_id=portfolio_id)

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
        portfolio = self.get_portfolio(token_bearer=token_bearer, portfolio_id=portfolio_id)

        portfolio_securities = PortfolioUtils.get_portfolio_security_values(
            database=self.database,
            portfolio=portfolio
        )

        return list(map(self.translate_portfolio_security, portfolio_securities))

    def get_portfolio(self, token_bearer: TokenModel, portfolio_id: UUID) -> DbPortfolio:
        """

        Args:
            token_bearer (TokenModel): access token
            portfolio_id (UUID): portfolio id

        Returns:
            DbPortfolio

        Raises:
            HTTPException, with status 404 if portfolio does not exist
            HTTPException, with status 401 if logged user does not have SSN defined
            HTTPException, with status 403 if logged user does not have proper permissions
        """
        if not AuthUtils.has_user_role(token_bearer=token_bearer):
            raise HTTPException(
                status_code=403,
                detail="This endpoint is not available for anonymous users"
            )

        portfolio = operations.find_portfolio(
            database=self.database,
            portfolio_id=portfolio_id
        )

        if not portfolio:
            raise HTTPException(
                status_code=404,
                detail=f"Portfolio {portfolio_id} not found"
            )

        user_ssn = AuthUtils.get_user_ssn(token_bearer=token_bearer)
        if not user_ssn:
            raise HTTPException(
                status_code=403,
                detail=f"Cannot resolve logged user SSN"
            )

        if user_ssn != portfolio.company.ssn:
            company_access = operations.find_company_access_by_ssn_and_company_id(
                database=self.database,
                ssn=user_ssn,
                company_id=portfolio.company.id
            )

            if not company_access:
                raise HTTPException(
                    status_code=403,
                    detail=f"No permission to find this portfolio"
                )

        return portfolio

    def translate_portfolio(self,
                            portfolio: DbPortfolio,
                            own_companies: List[DbCompany],
                            ) -> Portfolio:
        """
        Translates portfolio into REST resource

        Args:
            portfolio: portfolio to translate
            own_companies: list of companies that user owns

        Returns:
            REST resource
        """
        portfolio_values = PortfolioUtils.get_portfolio_values(
            database=self.database,
            portfolio=portfolio
        )

        own_company_ids = [company.id for company in own_companies]
        access_level = "OWNED" if portfolio.company_id in own_company_ids else "SHARED"

        total_amount = str(portfolio_values.total_amount) \
            if portfolio_values.total_amount is not None else "0"
        market_value_total = str(portfolio_values.market_value_total) \
            if portfolio_values.market_value_total is not None else "0"
        purchase_total = str(portfolio_values.purchase_total) \
            if portfolio_values.purchase_total is not None else "0"

        company_code = portfolio.company.original_id

        share_a = "10"  # 'A' type is for growth.
        share_b = "20"  # 'B' type is for profit.
        portfolio_key = PortfolioUtils.get_portfolio_key(portfolio.original_id)
        reference_a = PortfolioUtils.make_reference(share_a, company_code, portfolio_key)
        reference_b = PortfolioUtils.make_reference(share_b, company_code, portfolio_key)
        company_id = str(portfolio.company_id)

        return Portfolio(
            id=str(portfolio.id),
            companyId=company_id,
            accessLevel=access_level,
            name=portfolio.name,
            totalAmount=total_amount,
            marketValueTotal=market_value_total,
            purchaseTotal=purchase_total,
            aReference=reference_a,
            bReference=reference_b
        )

    def translate_portfolio_log(self, portfolio_log: DbPortfolioLog) -> PortfolioTransaction:
        target_security_id = None
        if portfolio_log.c_security_id is not None:
            target_security_id = str(portfolio_log.c_security_id)

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
    def translate_portfolio_security(portfolio_security_values: PortfolioSecurityValues) -> PortfolioSecurity:
        """
        Translates portfolio security into REST resource
        """
        return PortfolioSecurity(
            id=str(portfolio_security_values.security_id),
            amount=str(portfolio_security_values.total_amount),
            totalValue=str(portfolio_security_values.market_value_total),
            purchaseValue=str(portfolio_security_values.purchase_total)
        )
