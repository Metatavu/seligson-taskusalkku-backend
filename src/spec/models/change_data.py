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

        _1d_change: The _1d_change of this ChangeData [Optional].
        _1m_change: The _1m_change of this ChangeData [Optional].
        _1y_change: The _1y_change of this ChangeData [Optional].
        _3y_change: The _3y_change of this ChangeData [Optional].
        _5y_change: The _5y_change of this ChangeData [Optional].
        _10y_change: The _10y_change of this ChangeData [Optional].
        _15y_change: The _15y_change of this ChangeData [Optional].
        _20y_change: The _20y_change of this ChangeData [Optional].
    """
    _1d_change: Optional[float] = None
    _1m_change: Optional[float] = None
    _1y_change: Optional[float] = None
    _3y_change: Optional[float] = None
    _5y_change: Optional[float] = None
    _10y_change: Optional[float] = None
    _15y_change: Optional[float] = None
    _20y_change: Optional[float] = None


ChangeData.update_forward_refs()
