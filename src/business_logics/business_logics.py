from config.settings import Settings

settings = Settings()


def transaction_is_redemption(transaction_code: str) -> bool:
    """
    checks if a code is redemption code
    """
    return True if transaction_code == settings.REDEMPTION_CODE else False


def transaction_is_subscription(transaction_code: str) -> bool:
    """
    checks if a code is subscription code
    """
    return True if transaction_code == settings.SUBSCRIPTION_CODE else False


def get_transaction_codes_for_subscription_redemption() -> [str]:
    """
    return the subscription and redemption codes
    """
    return [settings.REDEMPTION_CODE, settings.SUBSCRIPTION_CODE]


def fund_is_subscribable(fund_original_id: int) -> bool:
    """
    verifies the fund id of 4444. This fund is not subscribable because ETF funds are not subscribable.
    """
    return fund_original_id not in settings.ETF_FUND_CODES
