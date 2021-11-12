# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, validator  # noqa: F401


class ChangeData(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    ChangeData - a model defined in OpenAPI

        change1d: The change1d of this ChangeData [Optional].
        change1m: The change1m of this ChangeData [Optional].
        change1y: The change1y of this ChangeData [Optional].
        change3y: The change3y of this ChangeData [Optional].
        change5y: The change5y of this ChangeData [Optional].
        change10y: The change10y of this ChangeData [Optional].
        change15y: The change15y of this ChangeData [Optional].
        change20y: The change20y of this ChangeData [Optional].
    """
    change1d: Optional[float] = None
    change1m: Optional[float] = None
    change1y: Optional[float] = None
    change3y: Optional[float] = None
    change5y: Optional[float] = None
    change10y: Optional[float] = None
    change15y: Optional[float] = None
    change20y: Optional[float] = None


ChangeData.update_forward_refs()
