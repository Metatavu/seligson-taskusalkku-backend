from pprint import pprint
from typing import Optional, List

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

    @pytest.mark.parametrize("auth", invalid_auths)
    def test_list_company_invalid_auth(self, client: TestClient, backend_mysql: MySqlContainer,
                                       keycloak: KeycloakContainer, auth: BearerAuth):
        self.assert_list_company_fail(
            client=client,
            expected_status=403,
            auth=auth
        )

    def test_find_company_anonymous(self, client: TestClient, backend_mysql: MySqlContainer,
                                    keycloak: KeycloakContainer, anonymous_auth: BearerAuth):
        self.assert_list_company_fail(
            client=client,
            expected_status=403,
            auth=anonymous_auth
        )

    def test_find_company_unauthorized(self, client: TestClient, backend_mysql: MySqlContainer,
                                       keycloak: KeycloakContainer):
        self.assert_list_company_fail(
            client=client,
            expected_status=403,
            auth=None
        )

    def test_list_company_access(self, client: TestClient, backend_mysql: MySqlContainer, keycloak: KeycloakContainer,
                                 user_1_auth: BearerAuth, user_2_auth: BearerAuth, user_3_auth: BearerAuth):

        with sql_backend_funds(backend_mysql), sql_backend_company(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_company_access(backend_mysql):

            user_1_companies = self.list_companies(
                client=client,
                auth=user_1_auth
            )

            assert len(user_1_companies) == 3
            assert user_1_companies[0]["id"] == "f0e88a2d-d773-46bd-b353-117a448abefd"
            assert user_1_companies[0]["accessLevel"] == "OWNED"
            assert user_1_companies[0]["name"] == "Company for 123"
            assert user_1_companies[1]["id"] == "05b189d1-3ce3-4830-9da0-176304142d85"
            assert user_1_companies[1]["accessLevel"] == "OWNED"
            assert user_1_companies[1]["name"] == "Company for 124"
            assert user_1_companies[2]["id"] == "64baed5c-9ebb-43d5-9af0-ba2c60025aaa"
            assert user_1_companies[2]["accessLevel"] == "OWNED"
            assert user_1_companies[2]["name"] == "Company for 125"

            user_2_companies = self.list_companies(
                client=client,
                auth=user_2_auth
            )

            assert len(user_2_companies) == 2
            assert user_2_companies[0]["id"] == "10dac398-4fec-4d02-9ca6-abf705a83cf4"
            assert user_2_companies[0]["accessLevel"] == "OWNED"
            assert user_2_companies[0]["name"] == "Company for 222"
            assert user_2_companies[1]["id"] == "feebf58a-d382-4645-9855-d7e3f7534103"
            assert user_2_companies[1]["accessLevel"] == "SHARED"
            assert user_2_companies[1]["name"] == "Company for 333"

            user_3_companies = self.list_companies(
                client=client,
                auth=user_3_auth
            )

            assert len(user_3_companies) == 1
            assert user_3_companies[0]["id"] == "feebf58a-d382-4645-9855-d7e3f7534103"
            assert user_3_companies[0]["accessLevel"] == "OWNED"

    @staticmethod
    def assert_find_company_fail(client: TestClient, expected_status: int, company_id: str,
                                 auth: Optional[BearerAuth]):
        """
        Assert that the find company endpoint fails with the expected status code.

        Args:
            client: The test client.
            expected_status: The expected status code.
            company_id: The company id.
            auth: The authentication.
        """
        if auth is None:
            response = client.get(f"/v1/companies/{company_id}")
        else:
            response = client.get(f"/v1/companies/{company_id}", auth=auth)

        assert expected_status == response.status_code

    @staticmethod
    def assert_list_company_fail(client: TestClient, expected_status: int, auth: Optional[BearerAuth]):
        """
        Assert that the find company endpoint fails with the expected status code.

        Args:
            client: The test client.
            expected_status: The expected status code.
            auth: The authentication.
        """
        if auth is None:
            response = client.get(f"/v1/companies")
        else:
            response = client.get(f"/v1/companies", auth=auth)

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

    @staticmethod
    def list_companies(client: TestClient, auth: BearerAuth) -> List[Dict[str, any]]:
        """Finds single company from the API

        Args:
            client (TestClient): client
            auth (BearerAuth): auth
        Returns:
             [Company]: single company
        """
        response = client.get(f"/v1/companies", auth=auth)
        assert response.status_code == 200
        return response.json(parse_float=Decimal)
