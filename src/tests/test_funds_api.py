import json

from starlette.testclient import TestClient

from .auth.auth import BearerAuth

from .fixtures.mysql import *
from .fixtures.users import *
from .fixtures.client import *

fund_1_id = "b4b48c6c-dc78-32cd-8b4b-bad38c9c23bf"
fund_2_id = "9654b4b6-8cda-3f5d-a9cf-ed687ee779e5"
fund_3_id = "024dedad-e688-3ea9-83d0-fefc7b1107f4"

invalid_uuids = ["potato", "`?%!", "äö", "Правда"]

class TestFunds:
    """Tests for funds endpoints
    """    

    def test_find_fund(self, client: TestClient, user_1_auth: BearerAuth):
      response = client.get("/v1/funds/{fund_id}".format(fund_id = fund_1_id), auth = user_1_auth)
      assert response.status_code == 200

      fund = response.json()
      assert fund_1_id == fund["id"]
      assert { "fi" : "Testirahasto 1", "sv" : "Testfond 1" } == fund["name"]
      assert { "fi": "Testirahasto 1 - pitkä nimi suomeksi", "sv": "Testfond 1 - långt namn på svenska " } == fund["long_name"]
      assert { "fi": "Testirahasto 1 - suomeksi", "sv": "Testfond 1 - på svenska " } == fund["short_name"]
      assert "#123456" == fund["color"] 
      assert 1 == fund["risk"] 
      assert None == fund["kiid"]
      assert None == fund["bank_receiver_name"]
      assert None == fund["group"]
      assert None == fund["price_date"]
      assert None == fund["a_share_value"]
      assert None == fund["b_share_value"]
      assert None == fund["change_data"]
      assert None == fund["profit_projection"]
      assert None == fund["profit_projection_date"]

    def test_find_fund_invalid_id(self, client: TestClient, user_1_auth: BearerAuth):          
          for id in invalid_uuids:
            response = client.get("/v1/funds/{fund_id}".format(fund_id = id), auth = user_1_auth)
            assert response.status_code == 400