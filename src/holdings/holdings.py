from decimal import Decimal
from typing import Optional, Dict, List
from uuid import UUID
from datetime import date, timedelta


class HoldingsException(Exception):
    """
    Exception for errors in holdings handling
    """
    pass


class Holdings:
    """Helper class for calculating portfolio holdings"""

    def __init__(self):
        """Constructor"""
        self.data: Dict[UUID, Dict[date, Decimal]] = {}
        self.day_amounts: Dict[UUID, Dict[date, Decimal]] = {}

    def add_holding(self, security_id: UUID, holding_date: date, amount: Decimal):
        """
        Marks day's holding amount for a security

        Args:
            security_id: security id
            holding_date: date
            amount: amount
        """
        if security_id is None:
            raise HoldingsException("Missing security id for holding")

        if security_id not in self.data:
            self.data[security_id] = {}

        if holding_date not in self.data[security_id]:
            self.data[security_id][holding_date] = Decimal(0)

        self.data[security_id][holding_date] += amount

    def calculate_amounts(self, start_date: date, end_date: date):
        """
        Calculates daily amounts for holdings. This method needs to be called before using get_day_sum method

        Args:
            start_date: start date for the date range
            end_date: end date for the date range
        """
        for security_id in self.get_security_ids():
            self.day_amounts[security_id] = {}
            security_min_date = self.get_security_min_date(security_id)

            if start_date > security_min_date:
                start_date = security_min_date

            total = Decimal(0)
            for i in range((end_date - start_date).days + 1):
                holding_date = start_date + timedelta(days=i)

                change = self.data[security_id].get(holding_date, 0)
                if change is not None:
                    total += change

                self.day_amounts[security_id][holding_date] = total

    def get_day_amount(self, security_id: UUID, holding_date: date) -> Optional[Decimal]:
        """
        Returns day's holding amount for a security
        Args:
            security_id: security id
            holding_date: date

        Returns: day's holding amount for a security

        """
        if security_id not in self.day_amounts:
            return None

        if holding_date not in self.day_amounts[security_id]:
            return None

        return self.day_amounts[security_id][holding_date]

    def get_day_sum(self, holding_date: date, currency_rates: Dict[UUID, Dict[date, Decimal]],
                    security_rates: Dict[UUID, Dict[date, Decimal]]):
        """
        Calculates daily sum of holdings using day's currency and security rates as multipliers
        Args:
            holding_date: date
            currency_rates: currency rates
            security_rates: security rates

        Returns: daily sum of holdings
        """
        result = Decimal(0)

        for security_id in self.get_security_ids():
            security_security_rates = security_rates[security_id]
            security_currency_rates = currency_rates[security_id]
            day_security_rate = security_security_rates.get(holding_date, None)
            day_currency_rate = security_currency_rates.get(holding_date, None)

            amount = self.get_day_amount(security_id=security_id, holding_date=holding_date)
            if amount is not None and day_security_rate is not None and day_currency_rate is not None:
                result += amount * day_security_rate / day_currency_rate

        return result

    def is_empty(self) -> bool:

        return not self.data

    def get_security_ids(self) -> List[UUID]:
        return list(self.data.keys())

    def get_min_date(self) -> Optional[date]:
        result = None
        for security_id in self.get_security_ids():
            min_date = self.get_security_min_date(security_id)
            if result is None or min_date < result:
                result = min_date
        return result

    def get_max_date(self) -> Optional[date]:
        result = None
        for security_id in self.get_security_ids():
            max_date = self.get_security_max_date(security_id)
            if result is None or max_date > result:
                result = max_date
        return result

    def get_security_min_date(self, security_id: UUID) -> Optional[date]:
        result = None

        if security_id not in self.data:
            return None

        security_holdings = self.data[security_id]
        for holding_date in security_holdings.keys():
            if result is None or holding_date < result:
                result = holding_date

        return result

    def get_security_max_date(self, security_id: UUID) -> Optional[date]:
        result = None

        if security_id not in self.data:
            return None

        security_holdings = self.data[security_id]
        for holding_date in security_holdings.keys():
            if result is None or holding_date > result:
                result = holding_date

        return result
