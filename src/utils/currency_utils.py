from decimal import Decimal
from sqlalchemy.orm import Session
from database import operations
from typing import List, Dict


class CurrencyUtils:
    """
    Utilities for currency handling
    """

    @staticmethod
    def get_currency_map(database: Session, currencies: List[str]) -> Dict[str, Decimal]:
        """
        Returns conversion map from currency to EUR
        Args:
            database: database session
            currencies: currencies to be returned

        Returns: conversion map from currency to EUR
        """
        currencies = list(filter(lambda x: x != "EUR", currencies))

        currency_rate_map = operations.get_currency_rate_map(
            database=database,
            currencies=currencies
        )

        currency_rate_map["EUR"] = Decimal(1)

        return currency_rate_map

