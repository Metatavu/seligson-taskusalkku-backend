from starlette.testclient import TestClient

from .auth.auth import BearerAuth

from .fixtures.keycloak import *
from .fixtures.mysql import *
from .fixtures.users import *
from .fixtures.client import *

class TestFunds:
    """Tests for funds endpoints
    """    

    def test_find_fund(self, client: TestClient, user_1_auth: BearerAuth):
      response = client.get("/v1/funds/D44C5F1E-F41B-45D6-B7A6-EF6BF7873E59", auth = user_1_auth)
      assert response.status_code == 200
