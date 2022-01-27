# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, validator  # noqa: F401


class SubscriptionBankAccount(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    SubscriptionBankAccount - a model defined in OpenAPI

        BankAccountName: The BankAccountName of this SubscriptionBankAccount [Optional].
        IBAN: The IBAN of this SubscriptionBankAccount [Optional].
        AccountNumberOldFormat: The AccountNumberOldFormat of this SubscriptionBankAccount [Optional].
        BIC: The BIC of this SubscriptionBankAccount [Optional].
        Currency: The Currency of this SubscriptionBankAccount [Optional].
    """
    BankAccountName: Optional[str] = None
    IBAN: Optional[str] = None
    AccountNumberOldFormat: Optional[str] = None
    BIC: Optional[str] = None
    Currency: Optional[str] = None


SubscriptionBankAccount.update_forward_refs()
