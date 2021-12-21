import uuid
from typing import Optional

from .constants import fund_ids, invalid_uuids, security_ids, invalid_auths
from .fixtures.backend_mysql import *  # noqa
from .fixtures.client import *  # noqa
from .fixtures.kafka import *  # noqa
from .fixtures.kafka_connect import *  # noqa
from .fixtures.salkku_mysql import *  # noqa
from .fixtures.sync import *  # noqa
from .fixtures.users import *  # noqa
from .fixtures.zookeeper import *  # noqa
from .utils.database import sql_backend_security, sql_backend_funds

import logging

logger = logging.getLogger(__name__)

security_1_data = {
    "id": security_ids["ACTIVETEST01"],
    "fundId": fund_ids["activetest01"],
    "name": {"fi": "Active test security 1 - fi", "sv": "Active test security 1 - sv"},
    "currency": "EUR"
}

security_5_data = {
    "id": security_ids["SPILTAN TEST"],
    "fundId": fund_ids["spiltan_test"],
    "name": {"fi": "Spiltan test security 1 - fi", "sv": "Spiltan test security 1 - sv"},
    "currency": "SEK"
}


class TestSecurities:
    """Tests for securities endpoints"""

    def test_find_security(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            security_id = security_1_data["id"]
            response = client.get(f"/v1/securities/{security_id}", auth=user_1_auth)
            assert response.status_code == 200
            security = response.json()
            assert security == security_1_data

    def test_find_security_not_found(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            security_id = uuid.uuid4()
            response = client.get(f"/v1/securities/{security_id}", auth=user_1_auth)
            assert response.status_code == 404

    def test_find_security_invalid_id(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            for invalid_uuid in invalid_uuids:
                url = f"/v1/securities/{invalid_uuid}"
                response = client.get(url, auth=user_1_auth)
                assert response.status_code == 400

    @pytest.mark.parametrize("auth", invalid_auths)
    def test_find_security_invalid_auth(self, client: TestClient, backend_mysql: MySqlContainer,
                                        keycloak: KeycloakContainer, auth: BearerAuth):
        self.assert_find_security_fail(
            client=client,
            expected_status=403,
            auth=auth,
            security_id=security_1_data["id"]
        )

    def test_find_security_anonymous(self, client: TestClient, backend_mysql: MySqlContainer,
                                     keycloak: KeycloakContainer, anonymous_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            security_id = security_1_data["id"]
            response = client.get(f"/v1/securities/{security_id}", auth=anonymous_auth)
            assert response.status_code == 200

    def test_find_security_unauthorized(self, client: TestClient, backend_mysql: MySqlContainer,
                                        keycloak: KeycloakContainer):
        self.assert_find_security_fail(
            client=client,
            expected_status=403,
            auth=None,
            security_id=security_1_data["id"]
        )

    def test_list_securities(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            response = client.get("/v1/securities", auth=user_1_auth)
            assert response.status_code == 200

            response_securities = response.json()

            assert 6 == len(response_securities)

            assert response_securities[0] == security_1_data
            assert response_securities[5] == security_5_data

    @pytest.mark.parametrize("auth", invalid_auths)
    def test_list_securities_invalid_auth(self, client: TestClient, backend_mysql: MySqlContainer,
                                          keycloak: KeycloakContainer, auth: BearerAuth):
        self.assert_list_securities_fail(
            client=client,
            expected_status=403,
            auth=auth
        )

    def test_list_securities_anonymous(self, client: TestClient, backend_mysql: MySqlContainer,
                                       keycloak: KeycloakContainer, anonymous_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            response = client.get(f"/v1/securities", auth=anonymous_auth)
            assert response.status_code == 200
            assert 6 == len(response.json())

    def test_list_securities_unauthorized(self, client: TestClient, backend_mysql: MySqlContainer,
                                          keycloak: KeycloakContainer):
        with sql_backend_funds(backend_mysql):
            self.assert_list_securities_fail(
                client=client,
                expected_status=403,
                auth=None
            )

    @staticmethod
    def assert_find_security_fail(client: TestClient, expected_status: int, security_id: str,
                                  auth: Optional[BearerAuth]):
        if auth is None:
            response = client.get(f"/v1/securities/{security_id}")
        else:
            response = client.get(f"/v1/securities/{security_id}", auth=auth)

        assert expected_status == response.status_code

    @staticmethod
    def assert_list_securities_fail(client: TestClient, expected_status: int, auth: Optional[BearerAuth]):
        if auth is None:
            response = client.get("/v1/securities")
        else:
            response = client.get("/v1/securities", auth=auth)

        assert expected_status == response.status_code
