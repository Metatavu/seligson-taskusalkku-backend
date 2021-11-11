from starlette.testclient import TestClient

from .auth.auth import BearerAuth

from .fixtures.mysql import *
from .fixtures.users import *
from .fixtures.client import *

fund_passivetest01_id = "03568d76-93f1-3a2d-9ed5-b95516546548"
fund_activetest01_id = "dc856547-449b-306e-80c9-05ef8a002a3a"
fund_balancedtst01_id = "3073d4fe-78cc-36ec-a7e0-9c24944030b0"
fund_fixedtest0_id = "8cd9b437-e524-3926-a3f9-969923cf51bd"
fund_dimetest01_id = "79f8da68-6bdc-3a24-acde-327aa14e2546"
fund_spiltan_test_id = "098a999d-65ae-3746-900b-b0b33a5d7d9c"

invalid_uuids = ["potato", "`?%!", "äö", "Правда"]


class TestFunds:
    """Tests for funds endpoints"""

    def test_find_fund(self, client: TestClient, user_1_auth: BearerAuth):
        response = client.get("/v1/funds/{fund_id}".format(fund_id = fund_passivetest01_id), auth = user_1_auth)
        assert response.status_code == 200

        fund = response.json()
        assert fund_passivetest01_id == fund["id"]
        assert {"fi": "Passive test fund 1 - fi", "sv": "Passive test fund 1 - en"} == fund["name"]
        assert {"fi": "Passive test fund 1 - fi, long", "sv": "Passive test fund 1 - en, long"} == fund["longName"]
        assert {"fi": "Passive test fund 1 - fi, short", "sv": "Passive test fund 1 - en, short"} == fund["shortName"]
        assert "#123456" == fund["color"] 
        assert 1 == fund["risk"] 
        assert None == fund["KIID"]
        assert None == fund["bankReceiverName"]
        assert "PASSIVE" == fund["group"]
        assert "2021-11-10" == fund["priceDate"]
        assert 1.2345 == fund["aShareValue"]
        assert 1.098 == fund["bShareValue"]
        assert 0.00 == fund["changeData"]["change1d"]
        assert -0.01 == fund["changeData"]["change1m"]
        assert -0.19 == fund["changeData"]["change1y"]
        assert -0.27 == fund["changeData"]["change3y"]
        assert -1.02 == fund["changeData"]["change5y"]
        assert 1.22 == fund["changeData"]["change10y"]
        assert 12.3 == fund["changeData"]["change15y"]
        assert 25.5 == fund["changeData"]["change20y"]
        assert -0.32 == fund["profitProjection"]
        assert "2021-10-12" == fund["profitProjectionDate"]

    def test_find_fund_invalid_id(self, client: TestClient, user_1_auth: BearerAuth):          
          for id in invalid_uuids:
            response = client.get("/v1/funds/{fund_id}".format(fund_id = id), auth = user_1_auth)
            assert response.status_code == 400