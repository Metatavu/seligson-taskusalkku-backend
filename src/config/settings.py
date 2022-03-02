from datetime import date
from decimal import Decimal

from pydantic import BaseSettings


class Settings(BaseSettings):
    LAST_FIM_DATE: date = date(1999, 1, 1)
    FIM_CONVERT_RATE: Decimal = Decimal(5.94573)
    ETF_FUND_CODES = [4444]
    MEETING_TIME_PERIOD = range(9, 17)
    SUBSCRIPTION_CODE = "11"
    REDEMPTION_CODE = "12"
    EURO_CURRENCY_CODE = "EUR"
