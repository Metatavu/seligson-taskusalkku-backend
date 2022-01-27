import os
import json
import logging

from typing import List, TypedDict, Optional, Dict
from csv import DictReader
from datetime import date, datetime

logger = logging.getLogger(__name__)


class BankInfo(TypedDict, total=False):
    """Defines a bank info entry"""
    bank_account_name: Optional[str]
    iban: Optional[str]
    account_number_old_format: Optional[str]
    bic: Optional[str]
    currency: Optional[str]


class FundMeta(TypedDict, total=False):
    """Defines a fund meta entry"""

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
    a_share_value: str
    b_share_value: str
    _1d_change: str
    _1m_change: str
    _1y_change: str
    _3y_change: str
    _5y_change: str
    _10y_change: str
    _15y_change: str
    _20y_change: str
    profit_projection: str
    profit_projection_date: date
    bank_info: Optional[List[BankInfo]]


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

    group_map = {
      "spiltan": "SPILTAN",
      "dimension": "DIMENSION",
      "fixedIncome": "FIXED_INCOME",
      "balanced": "BALANCED",
      "active": "ACTIVE",
      "passive": "PASSIVE"
    }

    def get_fund_meta_by_fund_id(self, fund_id: str) -> Optional[FundMeta]:
        """Returns fund meta entry for given fund code

        Args:
            fund_id (uuid): Fund id

        Returns:
            FundMeta: fund meta
        """
        return next((entry for entry in self.get_all_fund_metas() if entry["fund_id"] == fund_id), None)

    def get_all_fund_metas(self) -> List[FundMeta]:
        """Returns all fund metas

        Returns:
            List[FundMeta]: Fund metas
        """
        if not self.data:
            funds = self.load_funds()
            data: List[FundMeta] = []
            for (code, value) in funds.items():
                fund_meta = self.translate_fund_meta(
                                                     code=code,
                                                     fund_json_entry=value
                                                    )
                if fund_meta:
                    data.append(fund_meta)
            self.data = data

        return self.data

    def translate_fund_meta(self,
                            code: str,
                            fund_json_entry: FundJsonEntry
                            ) -> Optional[FundMeta]:
        """Translates single JSON file entry to FundMeta entry

        Args:
            code (str): Fund code
            fund_json_entry (FundJsonEntry): JSON entry

        Returns:
            FundMeta: FundMeta entry
        """
        fund_id = self.get_fund_id(fund_code=code)
        if not fund_id:
            return None

        group = self.get_fund_group(fund_code=code)
        values_basic = self.get_fund_values_basic_for_fund_id(fund_id=fund_id)
        funds_banks = self.load_subscription_bank_accounts()
        fund_bank_info = self.get_fund_bank_info(funds_banks=funds_banks, fund_id=fund_id)

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
                        fund_code=code,
                        fund_id=fund_id,
                        color=fund_json_entry["color"],
                        kiid=fund_json_entry.get("kiid", None),
                        long_name=fund_json_entry["longName"],
                        name=fund_json_entry["name"],
                        risk=fund_json_entry["risk"],
                        short_name=fund_json_entry["shortName"],
                        subs_name=fund_json_entry.get("subsName", None),
                        group=group,
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
                        profit_projection_date=profit_projection_date,
                        bank_info=fund_bank_info if fund_bank_info else None
                      )

    @staticmethod
    def parse_csv_date(csv_date: str) -> Optional[date]:
        """Parses date from CSV value

        Args:
            csv_date (str): CSV date value

        Returns:
            Optional[date]: date
        """
        if "-" == csv_date:
            return None

        return datetime.strptime(csv_date, "%d.%m.%Y").date()

    @staticmethod
    def parse_csv_float(csv_float: str) -> Optional[str]:
        """Parses float from CSV value

        Args:
            csv_float (str): CSV float value

        Returns:
            Optional[str]: parsed float as string
        """
        if "-" == csv_float:
            return None

        return csv_float.replace(",", ".")

    def get_fund_values_basic_for_fund_id(self,
                                          fund_id: str
                                          ) -> Dict[str, str]:
        """Resolves CSV row from basic values basic CSV for given fund_id

        Args:
            fund_id (str): fund id

        Returns:
            dict[str, str]: CSV row data
        """
        return next((entry for entry in self.get_fund_values_basic() if fund_id == entry["fund_id"]), None)

    def get_fund_bank_account_for_fund_id(self,
                                          fund_id: str
                                          ) -> Dict[str, str]:
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
        return self.load_file_as_json(os.environ["FUND_JSON"])

    def load_subscription_bank_accounts(self) -> Dict:
        """Loads subscription bank accounts JSON file

        Returns:
            dict: JSON object
        """
        return self.load_file_as_json(os.environ["SUBSCRIPTION_BANK_ACCOUNTS_JSON"])

    @staticmethod
    def load_file_as_json(environment_variable) -> Dict:
        """Loads a JSON file from a path set by environment variable

        Returns:
            dict: JSON object
        """
        with open(environment_variable) as json_file:
            return json.load(json_file)

    def get_fund_id(self, fund_code: str) -> Optional[str]:
        """Resolves fund id for given fund code

        Args:
            fund_code (str): fund code

        Returns:
            str: fund id for given fund code or None if not found
        """
        fund_options = self.get_fund_options()
        fund_id = fund_options["fundId"]
        try:
            fund_index = list(fund_id.values()).index(fund_code)
            return list(fund_id.keys())[fund_index]
        except ValueError:
            return None

    def get_fund_group(self, fund_code: str) -> Optional[str]:
        """Returns group for given fund code

        Args:
            fund_code (str): fund code

        Returns:
            Optional[str]: fund group or None if not found
        """
        fund_value_group = self.get_fund_value_group(fund_code=fund_code)
        if not fund_value_group:
            return None

        group = fund_value_group["group"]
        if not group:
            return None

        return self.group_map.get(group, None)

    def get_fund_value_group(self, fund_code: str) -> Optional[FundValueGroup]:
        """Resolves fund value group for given fund code

        Args:
            fund_code (str): fund code

        Returns:
            Optional[FundValueGroup]: fund value group
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

    @staticmethod
    def get_fund_values_basic() -> Optional[List[Dict[str, str]]]:
        """Returns fund values basic

        Returns:
            dict: fund values object
        """
        result = []

        with open(os.environ["FUND_VALUES_BASIC_CSV"]) as csv_file:
            rows = DictReader(csv_file, delimiter=";")
            for row in rows:
                basic_value = dict()
                for key, value in row.items():
                    basic_value[key.strip()] = value
                result.append(basic_value)

        return result

    def get_fund_bank_info(self, funds_banks, fund_id: str) -> List[BankInfo]:
        return [self.translate_fund_bank_info(fund_bank) for fund_bank in funds_banks if
                fund_id == str(fund_bank["FundID"])]

    @staticmethod
    def translate_fund_bank_info(fund_bank_info):
        return BankInfo(
            bank_account_name=fund_bank_info.get("BankAccountName", None),
            iban=fund_bank_info.get("IBAN", None),
            account_number_old_format=fund_bank_info.get("AccountNumber_OldFormat", None),
            bic=fund_bank_info.get("BIC", None),
            currency=fund_bank_info.get("Currency", None))
