from dataclasses import dataclass
from decimal import Decimal
from sqlalchemy.orm import Session
from database import operations
from database.models import Portfolio
from uuid import UUID
from typing import List
from utils.currency_utils import CurrencyUtils


@dataclass
class PortfolioSecurityValues:
    """Data class for portfolio security values query result"""
    security_id: UUID
    total_amount: Decimal
    purchase_total: Decimal
    market_value_total: Decimal


@dataclass
class PortfolioValues:
    """Data class for portfolio values query result"""
    total_amount: Decimal
    purchase_total: Decimal
    market_value_total: Decimal


class PortfolioUtils:

    @staticmethod
    def get_portfolio_values(database: Session, portfolio: Portfolio) -> PortfolioValues:
        """
        Returns calculated summary of portfolio values
        Args:
            database: database session
            portfolio: portfolio

        Returns:
            calculated summary of portfolio values
        """
        portfolio_security_values = PortfolioUtils.get_portfolio_security_values(database=database, portfolio=portfolio)
        total_amount = Decimal(0)
        purchase_total = Decimal(0)
        market_value_total = Decimal(0)
        for portfolio_security_value in portfolio_security_values:
            total_amount += portfolio_security_value.total_amount
            purchase_total += portfolio_security_value.purchase_total
            market_value_total += portfolio_security_value.market_value_total

        return PortfolioValues(
            total_amount=total_amount,
            purchase_total=purchase_total,
            market_value_total=market_value_total
        )

    @staticmethod
    def get_portfolio_security_values(database: Session, portfolio: Portfolio) -> List[PortfolioSecurityValues]:
        """
        Returns calculated values for portfolio securities. Values are returned in euros
        Args:
            database: database session
            portfolio: portfolio

        Returns:
            calculated values for portfolio securities
        """
        portfolio_security_values = operations.get_portfolio_security_values(
            database=database,
            portfolio=portfolio
        )

        currencies = list(map(lambda x: x.currency, portfolio_security_values))
        currency_rate_map = CurrencyUtils.get_currency_map(
            database=database,
            currencies=currencies
        )

        result = []

        for portfolio_security_value in portfolio_security_values:
            currency_rate = currency_rate_map[portfolio_security_value.currency]

            result.append(
                PortfolioSecurityValues(
                    security_id=portfolio_security_value.security_id,
                    total_amount=portfolio_security_value.total_amount,
                    purchase_total=portfolio_security_value.purchase_total,
                    market_value_total=portfolio_security_value.market_value_total / currency_rate
                )
            )

        return result

    @staticmethod
    def get_portfolio_key(original_portfolio_id: str) -> str:
        """

        Args:
            original_portfolio_id: string representing portfolio original id

        Returns:
            either 0001 if the portfolio is the main portfolio or in case of
            sub portfolio dd00 where dd represents a number between 01-99.
        """
        portfolio_id_parts = original_portfolio_id.split("_")
        if len(portfolio_id_parts) == 2:
            portfolio_key = portfolio_id_parts[1].zfill(2)
        else:
            portfolio_key = "00"

        return portfolio_key + "01"

    @staticmethod
    def make_reference(share: str, company_code: str, portfolio_key: str) -> str:
        """

        Args:
            share(str): string representing profit("10") or growth("20")
            company_code(str): original company code associated with the portfolio
            portfolio_key(str): string value generated from portfolio id

        Returns(str):
            value including the concatenation of input with an extra digit, which is
            formulated from input parameters.

        """
        multiplier = [7, 3, 1]
        sum_of_digits = 0
        stem = share + company_code + portfolio_key
        i = len(stem) - 1
        j = 0
        while i >= 0:
            sum_of_digits += int(stem[i]) * multiplier[j % 3]
            i -= 1
            j += 1
        final_number = (10 - (sum_of_digits % 10)) % 10
        return stem + str(final_number)
