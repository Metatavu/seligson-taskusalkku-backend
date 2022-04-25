from typing import Optional

from .fixtures.client import *  # noqa
from .fixtures.users import *  # noqa
from .fixtures.salkku_mysql import *  # noqa
from .fixtures.backend_mysql import *  # noqa
from .fixtures.sync import *  # noqa
from .fixtures.kafka import *  # noqa
from .fixtures.kafka_connect import *  # noqa
from .fixtures.zookeeper import *  # noqa
from decimal import Decimal

from .constants import invalid_auths, invalid_uuids

from .utils.database import sql_backend_company, sql_backend_security, sql_backend_funds, sql_backend_company_access

import logging

logger = logging.getLogger(__name__)


class TestCompanies:

    def test_find_company(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        """
        test to find company from company id
        """

        with sql_backend_funds(backend_mysql), sql_backend_company(backend_mysql):
            company_id = "f0e88a2d-d773-46bd-b353-117a448abefd"
            company = self.get_company(client=client, company_id=company_id, auth=user_1_auth)

            assert company_id == company["id"]
            assert "Company for 123" == company["name"]
            assert "OWNED" == company["accessLevel"]

    def test_find_company_invalid_id(self, client: TestClient, backend_mysql: MySqlContainer,
                                     user_1_auth: BearerAuth):
        for invalid_uuid in invalid_uuids:
            self.assert_find_company_fail(
                client=client,
                expected_status=400,
                company_id=invalid_uuid,
                auth=user_1_auth
            )

    @pytest.mark.parametrize("auth", invalid_auths)
    def test_find_company_invalid_auth(self, client: TestClient, backend_mysql: MySqlContainer,
                                       keycloak: KeycloakContainer, auth: BearerAuth):
        self.assert_find_company_fail(
            client=client,
            expected_status=403,
            company_id="f0e88a2d-d773-46bd-b353-117a448abefd",
            auth=auth
        )

    def test_find_company_anonymous(self, client: TestClient, backend_mysql: MySqlContainer,
                                    keycloak: KeycloakContainer, anonymous_auth: BearerAuth):
        self.assert_find_company_fail(
            client=client,
            expected_status=403,
            company_id="f0e88a2d-d773-46bd-b353-117a448abefd",
            auth=anonymous_auth
        )

    def test_find_company_unauthorized(self, client: TestClient, backend_mysql: MySqlContainer,
                                       keycloak: KeycloakContainer):
        self.assert_find_company_fail(
            client=client,
            expected_status=403,
            company_id="f0e88a2d-d773-46bd-b353-117a448abefd",
            auth=None
        )

    def test_find_company_wrong_user(self, client: TestClient, backend_mysql: MySqlContainer,
                                     keycloak: KeycloakContainer, user_2_auth: BearerAuth, user_3_auth: BearerAuth):

        with sql_backend_funds(backend_mysql), sql_backend_company(backend_mysql), \
                sql_backend_security(backend_mysql):

            self.assert_find_company_fail(
                client=client,
                expected_status=403,
                company_id="f0e88a2d-d773-46bd-b353-117a448abefd",
                auth=user_2_auth
            )

            self.assert_find_company_fail(
                client=client,
                expected_status=403,
                company_id="f0e88a2d-d773-46bd-b353-117a448abefd",
                auth=user_3_auth
            )

    def test_find_company_access(self, client: TestClient, backend_mysql: MySqlContainer, keycloak: KeycloakContainer,
                                 user_1_auth: BearerAuth, user_2_auth: BearerAuth, user_3_auth: BearerAuth):

        with sql_backend_funds(backend_mysql), sql_backend_company(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_company_access(backend_mysql):

            owned_company = self.get_company(
                client=client,
                company_id="10dac398-4fec-4d02-9ca6-abf705a83cf4",
                auth=user_2_auth
            )

            assert owned_company is not None
            assert "OWNED" == owned_company["accessLevel"]

            shared_company = self.get_company(
                client=client,
                company_id="feebf58a-d382-4645-9855-d7e3f7534103",
                auth=user_2_auth
            )

            assert shared_company is not None
            assert "SHARED" == shared_company["accessLevel"]

            self.assert_find_company_fail(
                client=client,
                company_id="10dac398-4fec-4d02-9ca6-abf705a83cf4",
                auth=user_1_auth,
                expected_status=403
            )

    @staticmethod
    def assert_find_company_fail(client: TestClient, expected_status: int, company_id: str,
                                 auth: Optional[BearerAuth]):
        if auth is None:
            response = client.get(f"/v1/companies/{company_id}")
        else:
            response = client.get(f"/v1/companies/{company_id}", auth=auth)

        assert expected_status == response.status_code

    @staticmethod
    def get_company(client: TestClient, company_id: str, auth: BearerAuth) -> Dict[str, any]:
        """Finds single company from the API

        Args:
            client (TestClient): client
            company_id (str): company id
            auth (BearerAuth): auth
        Returns:
             [Company]: single company
        """
        response = client.get(f"/v1/companies/{company_id}", auth=auth)
        assert response.status_code == 200
        return response.json(parse_float=Decimal)
