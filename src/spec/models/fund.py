# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, validator  # noqa: F401
from spec.models.change_data import ChangeData
from spec.models.fund_group import FundGroup
from spec.models.localized_value import LocalizedValue
from spec.models.subscription_bank_account import SubscriptionBankAccount


class Fund(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    Fund - a model defined in OpenAPI

        id: The id of this Fund [Optional].
        name: The name of this Fund.
        longName: The longName of this Fund [Optional].
        shortName: The shortName of this Fund [Optional].
        bankReceiverName: The bankReceiverName of this Fund [Optional].
        group: The group of this Fund [Optional].
        priceDate: The priceDate of this Fund [Optional].
        aShareValue: The aShareValue of this Fund [Optional].
        bShareValue: The bShareValue of this Fund [Optional].
        changeData: The changeData of this Fund [Optional].
        profitProjection: The profitProjection of this Fund [Optional].
        profitProjectionDate: The profitProjectionDate of this Fund [Optional].
        color: The color of this Fund [Optional].
        risk: The risk of this Fund [Optional].
        KIID: The KIID of this Fund [Optional].
        subscriptionBankAccounts: The subscriptionBankAccounts of this Fund [Optional].
        subscribable: The subscribable of this Fund [Optional].
    """
    id: Optional[str] = None
    name: LocalizedValue
    longName: Optional[LocalizedValue] = None
    shortName: Optional[LocalizedValue] = None
    bankReceiverName: Optional[str] = None
    group: Optional[FundGroup] = None
    priceDate: Optional[date] = None
    aShareValue: Optional[str] = None
    bShareValue: Optional[str] = None
    changeData: Optional[ChangeData] = None
    profitProjection: Optional[str] = None
    profitProjectionDate: Optional[date] = None
    color: Optional[str] = None
    risk: Optional[int] = None
    KIID: Optional[LocalizedValue] = None
    subscriptionBankAccounts: Optional[List[SubscriptionBankAccount]] = None
    subscribable: Optional[bool] = None

    @classmethod
    @validator("a_share_value")
    def a_share_value_pattern(cls, value):
        assert value is not None and re.match(r"^[+-]?([0-9]+\.?[0-9]*|\.[0-9]+)$", value)
        return value

    @classmethod
    @validator("b_share_value")
    def b_share_value_pattern(cls, value):
        assert value is not None and re.match(r"^[+-]?([0-9]+\.?[0-9]*|\.[0-9]+)$", value)
        return value

    @classmethod
    @validator("profit_projection")
    def profit_projection_pattern(cls, value):
        assert value is not None and re.match(r"^[+-]?([0-9]+\.?[0-9]*|\.[0-9]+)$", value)
        return value


Fund.update_forward_refs()
