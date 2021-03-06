# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, validator  # noqa: F401
from spec.models.company_access_level import CompanyAccessLevel


class Company(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    Company - a model defined in OpenAPI

        id: The id of this Company [Optional].
        name: The name of this Company.
        accessLevel: The accessLevel of this Company.
    """
    id: Optional[str] = None
    name: str
    accessLevel: CompanyAccessLevel


Company.update_forward_refs()
