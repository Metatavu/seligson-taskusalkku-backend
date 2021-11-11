import os
import json
import logging

from typing import List, TypedDict, Optional, Dict
from uuid import UUID, uuid3
from csv import DictReader
from datetime import date, datetime

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
    price_date: date
    a_share_value: float
    b_share_value: float
    _1d_change: float
    _1m_change: float
    _1y_change: float
    _3y_change: float
    _5y_change: float
    _10y_change: float
    _15y_change: float
    _20y_change: float
    profit_projection: float
    profit_projection_date: date


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
    fundId: Dict[str, str]
    fundKey: Dict[str, str]
    fundValueGroups: List[FundValueGroup]


class FundsMetaController:
    """Funds meta controller"""

    data: Optional[List[FundMeta]] = None
    fund_options: Optional[FundOptions] = None
    fund_values_basic: Optional[List[Dict[str, str]]] = None
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
        return next((entry for entry in self.get_all_fund_metas() if entry["id"] == fund_id), None)

    def get_fund_meta_by_fund_code(self, fund_code: str) -> Optional[FundMeta]:
        """Returns fund meta entry for given fund code

        Args:
            fund_code (str): Fund code

        Returns:
            FundMeta: fund meta
        """
        return next((entry for entry in self.get_all_fund_metas() if entry["code"] == fund_code), None)

    def get_all_fund_metas(self) -> List[FundMeta]:
        """Returns fund metas

        Returns:
            List[FundMeta]: Fund metas
        """
        if not self.data:
            funds = self.load_funds()

            data: List[FundMeta] = []
            for (code, value) in funds.items():
                fund_meta = self.translate_fund_meta(code=code, fund_json_entry=value)
                data.append(fund_meta)
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
        fund_id = self.get_fund_id(fund_code=code)
        values_basic = self.get_fund_values_basic_for_fund_id(fund_id=fund_id)
        price_date = self.parse_csv_date(values_basic["price_date"])
        a_share_value = self.parse_csv_float(values_basic["a_share_value"])
        b_share_value = self.parse_csv_float(values_basic["b_share_value"])
        _1d_change = self.parse_csv_float(values_basic["1d_change"])
        _1m_change = self.parse_csv_float(values_basic["1m_change"])
        _1y_change = self.parse_csv_float(values_basic["1y_change"])
        _3y_change = self.parse_csv_float(values_basic["3y_change"])
        _5y_change = self.parse_csv_float(values_basic["5y_change"])
        _10y_change = self.parse_csv_float(values_basic["10y_change"])
        _15y_change = self.parse_csv_float(values_basic["15y_change"])
        _20y_change = self.parse_csv_float(values_basic["20y_change"])
        profit_projection = self.parse_csv_float(values_basic["profit_projection"])
        profit_projection_date = self.parse_csv_date(values_basic["profit_projection_date"])

        return FundMeta(
                        id=self.create_id(fund_code=code),
                        fund_code=code,
                        fund_id=fund_id,
                        color=fund_json_entry["color"],
                        kiid=fund_json_entry.get("kiid", None),
                        long_name=fund_json_entry["longName"],
                        name=fund_json_entry["name"],
                        risk=fund_json_entry["risk"],
                        short_name=fund_json_entry["shortName"],
                        subs_name=fund_json_entry.get("subsName", None),
                        group=self.group_map[group["group"]],
                        price_date=price_date,
                        a_share_value=a_share_value,
                        b_share_value=b_share_value,
                        _1d_change=_1d_change,
                        _1m_change=_1m_change,
                        _1y_change=_1y_change,
                        _3y_change=_3y_change,
                        _5y_change=_5y_change,
                        _10y_change=_10y_change,
                        _15y_change=_15y_change,
                        _20y_change=_20y_change,
                        profit_projection=profit_projection,
                        profit_projection_date=profit_projection_date
                      )

    def parse_csv_date(self, str: str) -> Optional[date]:
        """Parses date from CSV value

        Args:
            str (str): CSV value

        Returns:
            Optional[date]: date
        """
        if "-" == str:
            return None

        return datetime.strptime(str, "%d.%m.%Y").date()

    def parse_csv_float(self, str: str) -> Optional[float]:
        """Parses float from CSV value

        Args:
            str (str): CSV value

        Returns:
            Optional[float]: float
        """
        if "-" == str:
            return None

        return float(str.replace(",", "."))

    def get_fund_values_basic_for_fund_id(self, fund_id: str) -> Dict[str, str]:
        """Resolves CSV row from basic values basic CSV for given fund_id

        Args:
            fund_id (str): fund id

        Returns:
            dict[str, str]: CSV row data
        """
        return next((entry for entry in self.get_fund_values_basic() if fund_id == entry["fund_id"]), None)

    def load_funds(self) -> Dict:
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

    def get_fund_values_basic(self) -> Dict:
        """Returns fund values basic

        Returns:
            dict: fund values object
        """
        if not self.fund_values_basic:
            with open(os.environ["FUND_VALUES_BASIC_CSV"]) as csv_file:
                rows = DictReader(csv_file, delimiter=";")
                self.fund_values_basic = []
                for row in rows:
                    basic_value = dict()
                    for key, value in row.items():
                        basic_value[key.strip()] = value
                    self.fund_values_basic.append(basic_value)

        return self.fund_values_basic

    def create_id(self, fund_code: str) -> UUID:
        """Creates UUID from fund code

        Args:
            name (str): [description]

        Returns:
            UUID: [description]
        """
        return uuid3(uuid_namespace, fund_code)
