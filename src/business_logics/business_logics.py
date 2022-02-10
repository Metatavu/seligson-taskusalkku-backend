def transaction_is_redemption(transaction_code: str) -> bool:
    """
    checks if a code is redemption code
    """
    return True if transaction_code == "12" else False


def transaction_is_subscription(transaction_code: str) -> bool:
    """
    checks if a code is subscription code
    """
    return True if transaction_code == "11" else False


def get_transaction_codes_for_subscription_redemption() -> [str]:
    """
    return the subscription and redemption codes
    """
    return ["11", "12"]


def fund_is_subscribable(fund_code: str) -> bool:
    """
    verifies the specific case of HEX25ETF. This fund is not subscribable because ETF funds are not subscribable.
    """
    return fund_code != "HEX25ETF"
