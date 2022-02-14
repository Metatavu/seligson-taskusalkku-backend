from typing import Dict
from ..utils.fund_utils import FundUtils


class TestFundUtils:
    """
    Tests for fund utils class
    """

    def test_long_fund_names(self):
        """Tests get_fund_long_name_from_security_name method"""
        expect_longs: Dict[str, str] = {
            "Seligson & Co Suomi Indeksirahasto (A)": "Seligson & Co Suomi Indeksirahasto",
            "Seligson & Co Finland Index Fund (A)": "Seligson & Co Finland Index Fund",
            "Seligson & Co Finland Indexfond (A)": "Seligson & Co Finland Indexfond",
            "LähiTapiola Maailma 20 (A)": "LähiTapiola Maailma 20",
            "LocalTapiola World 20 (A)": "LocalTapiola World 20",
            "LokalTapiola Världen 20 (A)": "LokalTapiola Världen 20",
            "Sijoitusrahasto Phoenix K": "Sijoitusrahasto Phoenix K",
            "Phoenix Fund K": "Phoenix Fund K",
            "Placeringsfonden Phoenix K": "Placeringsfonden Phoenix K",
            "Seligson & Co Phoebus B(H)": "Seligson & Co Phoebus",
            "LähiTapiola Pohjoismaat ESG (A) ent. Skandinavia": "LähiTapiola Pohjoismaat ESG",
            "LocalTapiola ESG Nordics (A)": "LocalTapiola ESG Nordics",
            "LokalTapiola Norden ESG (A)": "LokalTapiola Norden ESG",
            "Seligson & Co Euro-obligaatio (VA)": "Seligson & Co Euro-obligaatio",
            "Seligson & Co Euro Bond Fund (VA)": "Seligson & Co Euro Bond Fund",
            "Seligson & Co Euroobligation (VA)": "Seligson & Co Euroobligation",
            "Seligson & Co OMX pörssinoteerattu rahasto UCITS":  "Seligson & Co OMX pörssinoteerattu rahasto UCITS",
            "Seligson & Co OMX Exchange Traded Fund UCITS ETF": "Seligson & Co OMX Exchange Traded Fund UCITS ETF",
            "Seligson & Co OMX börshandlad fond UCITS ETF": "Seligson & Co OMX börshandlad fond UCITS ETF"
        }

        for security_name, expected in expect_longs.items():
            assert FundUtils.get_fund_long_name_from_security_name(security_name=security_name) == expected

    def test_short_fund_names(self):
        """Tests get_fund_short_name_from_security_name method"""
        expect_shorts: Dict[str, str] = {
            "Seligson & Co Suomi Indeksirahasto (A)": "Suomi Indeksirahasto",
            "Seligson & Co Finland Index Fund (A)": "Finland Index Fund",
            "Seligson & Co Finland Indexfond (A)": "Finland Indexfond",
            "LähiTapiola Maailma 20 (A)": "Maailma 20",
            "LocalTapiola World 20 (A)": "World 20",
            "LokalTapiola Världen 20 (A)": "Världen 20",
            "Sijoitusrahasto Phoenix K": "Sijoitusrahasto Phoenix K",
            "Phoenix Fund K": "Phoenix Fund K",
            "Placeringsfonden Phoenix K": "Placeringsfonden Phoenix K",
            "Seligson & Co Phoebus B(H)": "Phoebus",
            "LähiTapiola Pohjoismaat ESG (A) ent. Skandinavia": "Pohjoismaat ESG",
            "LocalTapiola ESG Nordics (A)": "ESG Nordics",
            "LokalTapiola Norden ESG (A)": "Norden ESG",
            "Seligson & Co Euro-obligaatio (VA)": "Euro-obligaatio",
            "Seligson & Co Euro Bond Fund (VA)": "Euro Bond Fund",
            "Seligson & Co Euroobligation (VA)": "Euroobligation",
            "Seligson & Co OMX pörssinoteerattu rahasto UCITS":  "OMX pörssinoteerattu rahasto UCITS",
            "Seligson & Co OMX Exchange Traded Fund UCITS ETF": "OMX Exchange Traded Fund UCITS ETF",
            "Seligson & Co OMX börshandlad fond UCITS ETF": "OMX börshandlad fond UCITS ETF"
        }

        for security_name, expected in expect_shorts.items():
            assert FundUtils.get_fund_short_name_from_security_name(security_name=security_name) == expected
