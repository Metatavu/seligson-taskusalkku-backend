import os
import json
import logging

from typing import List, TypedDict, Optional
from uuid import UUID, uuid3

logger = logging.getLogger(__name__)

uuid_namespace = UUID("409C9B21-6711-4134-8BA9-C48DD0B5C9EC")


class FundMeta(TypedDict, total=False):
    """Defines a fund meta entry"""

    id: UUID
    fund_id: str
    fund_code: str
    name: List[str]
    subs_name: Optional[str]
    long_name: List[str]
    short_name: List[str]
    color: str
    risk: int
    kiid: Optional[List[str]]
    group: str


class FundJsonEntry(TypedDict, total=False):
    """Defines a fund meta entry in funds file"""

    name: List[str]
    subsName: Optional[str]
    longName: List[str]
    shortName: List[str]
    color: str
    risk: int
    kiid: Optional[List[str]]


class FundValueGroup(TypedDict):
    """Defines a fund value group in fund options file """
    group: str
    name: List[str]
    funds: List[str]


class FundOptions(TypedDict):
    """Defines fund options file structure"""
    fundId: dict
    fundKey: dict
    fundValueGroups: List[FundValueGroup]


class FundsMetaController:
    """Funds meta controller"""

    data: List[FundMeta] = None
    fund_options: dict = None
    group_map = {
      "spiltan": "SPILTAN",
      "dimension": "DIMENSION",
      "fixedIncome": "FIXED_INCOME",
      "balanced": "BALANCED",
      "active": "ACTIVE",
      "passive": "PASSIVE"
    }

    def get_fund_meta_by_fund_id(self, fund_id: UUID) -> Optional[FundMeta]:
        """Returns fund meta entry for given fund id

        Args:
            fund_id (uuid): Fund id

        Returns:
            FundMeta: fund meta
        """
        return next((entry for entry in self.get_funds_meta() if entry["id"] == fund_id), None)

    def get_fund_meta_by_fund_code(self, fund_code: str) -> Optional[FundMeta]:
        """Returns fund meta entry for given fund code

        Args:
            fund_code (str): Fund code

        Returns:
            FundMeta: fund meta
        """
        return next((entry for entry in self.get_funds_meta() if entry["code"] == fund_code), None)

    def get_funds_meta(self) -> List[FundMeta]:
        """Returns fund metas

        Returns:
            List[FundMeta]: Fund metas
        """
        if not self.data:
            funds = self.load_funds()

            data: List[FundMeta] = []
            for (code, value) in funds.items():
                data.append(self.translate_fund_meta(code = code, fund_json_entry = value))
            self.data = data

        return self.data

    def translate_fund_meta(self, code: str, fund_json_entry: FundJsonEntry) -> FundMeta:
        """Translates single JSON file entry to FundMeta entry

        Args:
            code (str): Fund code
            entry (FundJsonEntry): JSON entry

        Returns:
            FundMeta: FundMeta entry
        """
        group = self.get_fund_group(fund_code=code)

        return FundMeta(
                        id=self.create_id(fund_code=code),
                        fund_code=code,
                        fund_id=self.get_fund_id(fund_code=code),
                        color=fund_json_entry["color"],
                        kiid=fund_json_entry.get("kiid", None),
                        long_name=fund_json_entry["longName"],
                        name=fund_json_entry["name"],
                        risk=fund_json_entry["risk"],
                        short_name=fund_json_entry["shortName"],
                        subs_name=fund_json_entry.get("subsName", None),
                        group=self.group_map[group["group"]]
                      )

    def load_funds(self) -> dict:
        """Loads fund JSON file

        Returns:
            dict: JSON object
        """
        with open(os.environ["FUND_JSON"]) as json_file:
            return json.load(json_file)

    def get_fund_id(self, fund_code: str) -> str:
        """Resolves fund id for given fund code

        Args:
            fund_code (str): fund code

        Returns:
            str: fund id for given fund code
        """
        fund_options = self.get_fund_options()
        fund_id = fund_options["fundId"]
        return list(fund_id.keys())[list(fund_id.values()).index(fund_code)]

    def get_fund_group(self, fund_code: str) -> FundValueGroup:
        """Resolves fund group for given fund code

        Args:
            fund_code (str): fund code

        Returns:
            FundValueGroup: fund group
        """
        fund_options = self.get_fund_options()
        groups = fund_options["fundValueGroups"]
        return next((group for group in groups if fund_code in group["funds"]), None)

    def get_fund_options(self) -> FundOptions:
        """Returns fund options

        Returns:
            dict: JSON object
        """
        if not self.fund_options:
            with open(os.environ["FUND_OPTIONS_JSON"]) as json_file:
                self.fund_options = json.load(json_file)

        return self.fund_options

    def create_id(self, fund_code: str) -> UUID:
        """Creates UUID from fund code

        Args:
            name (str): [description]

        Returns:
            UUID: [description]
        """
        return uuid3(uuid_namespace, fund_code)
