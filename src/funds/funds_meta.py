import os
import json

from typing import List, TypedDict, Optional
from uuid import UUID, uuid3

uuid_namespace = UUID("409C9B21-6711-4134-8BA9-C48DD0B5C9EC")

class FundMeta(TypedDict, total=False):
    """Defines a fund meta entry"""

    id: UUID
    code: str
    name: List[str]
    subs_name: Optional[str]
    long_name: List[str]
    short_name: List[str]
    color: str
    risk: int
    kiid: Optional[List[str]]

class FundMetaJsonEntry(TypedDict, total=False):
    """Defines a fund meta entry in JSON file"""

    name: List[str]
    subsName: Optional[str]
    longName: List[str]
    shortName: List[str]
    color: str
    risk: int
    kiid: Optional[List[str]]

class FundsMetaController:
    """Funds meta controller
    """    

    data: List[FundMeta] = None

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
            json = self.load_json()
            data: List[FundMeta] = []
            for (code, value) in json.items():
              data.append(self.translate_fund_meta(code = code, entry = value))
            self.data = data

        return self.data

    def translate_fund_meta(self, code: str, entry: FundMetaJsonEntry) -> FundMeta:
        """Translates single JSON file entry to FundMeta entry

        Args:
            code (str): Fund code
            entry (FundMetaJsonEntry): JSON entry

        Returns:
            FundMeta: FundMeta entry
        """      
        return FundMeta(
                        id = self.uuid_from_string(fund_code = code),
                        code = code,
                        color = entry["color"],
                        kiid = entry.get("kiid", None),
                        long_name = entry["longName"],
                        name = entry["name"],
                        risk = entry["risk"],
                        short_name = entry["shortName"],
                        subs_name = entry.get("subsName", None)
                      )

    def load_json(self) -> dict:
        """Loads fund meta JSON file

        Returns:
            dict: JSON object
        """        
        with open(os.environ["FUND_META_JSON"]) as json_file:
            return json.load(json_file)

    def uuid_from_string(self, fund_code: str) -> UUID:
        """Creates UUID from fund code

        Args:
            name (str): [description]

        Returns:
            UUID: [description]
        """        
        return uuid3(uuid_namespace, fund_code)

