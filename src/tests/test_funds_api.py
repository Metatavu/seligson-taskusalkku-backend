from typing import List

from .utils.database import sql_backend_funds, sql_backend_security

from .constants import fund_ids, invalid_uuids, invalid_auths

from .fixtures.client import *  # noqa
from .fixtures.users import *  # noqa
from .fixtures.salkku_mysql import *  # noqa
from .fixtures.funds_mssql import *  # noqa
from .fixtures.backend_mysql import *  # noqa
from .fixtures.sync import *  # noqa
from .fixtures.kafka import *  # noqa
from .fixtures.kafka_connect import *  # noqa
from .fixtures.zookeeper import *  # noqa
import logging

logger = logging.getLogger(__name__)


class TestFunds:
    """Tests for funds endpoints"""

    def test_find_fund(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            fund_id = fund_ids["passivetest01"]
            response = client.get(f"/v1/funds/{fund_id}", auth=user_1_auth)
            assert response.status_code == 200

            fund = response.json()
            assert fund_id == fund["id"]
            assert "Seligson & Co FI - Passive test 1" == fund["name"]["fi"]
            assert "Seligson & Co SV - Passive test 1" == fund["name"]["sv"]
            assert "Seligson & Co EN - Passive test 1" == fund["name"]["en"]
            assert "Seligson & Co FI - Passive test 1" == fund["longName"]["fi"]
            assert "Seligson & Co SV - Passive test 1" == fund["longName"]["sv"]
            assert "Seligson & Co EN - Passive test 1" == fund["longName"]["en"]
            assert "FI - Passive test 1" == fund["shortName"]["fi"]
            assert "SV - Passive test 1" == fund["shortName"]["sv"]
            assert "EN - Passive test 1" == fund["shortName"]["en"]
            assert "#123456" == fund["color"]
            assert 1 == fund["risk"]
            assert "https://example.com/PASSIVETESTFI" == fund["KIID"]["fi"]
            assert "https://example.com/PASSIVETESTSV" == fund["KIID"]["sv"]
            assert "https://example.com/PASSIVETESTEN" == fund["KIID"]["en"]
            assert "Passive test fund 1 - subs" == fund["bankReceiverName"]
            assert "PASSIVE" == fund["group"]
            assert "2021-11-10" == fund["priceDate"]
            assert "1.2345" == fund["aShareValue"]
            assert "1.098" == fund["bShareValue"]
            assert "0.00" == fund["changeData"]["change1d"]
            assert "-0.01" == fund["changeData"]["change1m"]
            assert "-0.19" == fund["changeData"]["change1y"]
            assert "-0.27" == fund["changeData"]["change3y"]
            assert "-1.02" == fund["changeData"]["change5y"]
            assert "1.22" == fund["changeData"]["change10y"]
            assert "12.3" == fund["changeData"]["change15y"]
            assert "25.5" == fund["changeData"]["change20y"]
            assert "-0.32" == fund["profitProjection"]
            assert "2021-10-12" == fund["profitProjectionDate"]

            assert "fund 123 / Bank A" == fund["subscriptionBankAccounts"][0]["BankAccountName"]
            assert "FI0112345678901123" == fund["subscriptionBankAccounts"][0]["IBAN"]
            assert "12345678901123" == fund["subscriptionBankAccounts"][0]["AccountNumberOldFormat"]
            assert "ABCDFIAA" == fund["subscriptionBankAccounts"][0]["BIC"]
            assert "EUR" == fund["subscriptionBankAccounts"][0]["Currency"]
            assert "fund 123 / Bank B" == fund["subscriptionBankAccounts"][1]["BankAccountName"]
            assert "FI0112345678902123" == fund["subscriptionBankAccounts"][1]["IBAN"]
            assert "12345678902123" == fund["subscriptionBankAccounts"][1]["AccountNumberOldFormat"]
            assert "IJKLFIBB" == fund["subscriptionBankAccounts"][1]["BIC"]
            assert "EUR" == fund["subscriptionBankAccounts"][2]["Currency"]
            assert "fund 123 / Bank C" == fund["subscriptionBankAccounts"][2]["BankAccountName"]
            assert "FI0112345678903123" == fund["subscriptionBankAccounts"][2]["IBAN"]
            assert "12345678903123" == fund["subscriptionBankAccounts"][2]["AccountNumberOldFormat"]
            assert "MNOPFICC" == fund["subscriptionBankAccounts"][2]["BIC"]
            assert "EUR" == fund["subscriptionBankAccounts"][2]["Currency"]
            assert fund["subscribable"]

    def test_find_etf_fund(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            fund_id = fund_ids["HEX25ETF"]
            response = client.get(f"/v1/funds/{fund_id}", auth=user_1_auth)
            assert response.status_code == 200

            fund = response.json()
            assert fund_id == fund["id"]
            assert not fund["subscribable"]

    def test_find_fund_no_bank_details(self, client: TestClient, backend_mysql: MySqlContainer,
                                       user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            fund_id = fund_ids["activetest01"]
            response = client.get(f"/v1/funds/{fund_id}", auth=user_1_auth)
            assert response.status_code == 200

            fund = response.json()
            assert fund_id == fund["id"]
            assert fund["subscriptionBankAccounts"] is None

    def test_find_fund_partial_bank_details(self, client: TestClient, backend_mysql: MySqlContainer,
                                            user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            fund_id = fund_ids["balancedtst01"]
            response = client.get(f"/v1/funds/{fund_id}", auth=user_1_auth)
            assert response.status_code == 200

            fund = response.json()
            assert fund_id == fund["id"]
            assert "fund 345 / Bank A" == fund["subscriptionBankAccounts"][0]["BankAccountName"]
            assert fund["subscriptionBankAccounts"][0]["IBAN"] is None
            assert "18765432101345" == fund["subscriptionBankAccounts"][0]["AccountNumberOldFormat"]
            assert "ABCDFIAA" == fund["subscriptionBankAccounts"][0]["BIC"]
            assert "EUR" == fund["subscriptionBankAccounts"][0]["Currency"]
            assert "fund 345 / Bank C" == fund["subscriptionBankAccounts"][1]["BankAccountName"]
            assert fund["subscriptionBankAccounts"][1]["AccountNumberOldFormat"] is None
            assert "FI0112345678903123" == fund["subscriptionBankAccounts"][1]["IBAN"]
            assert "MNOPFICC" == fund["subscriptionBankAccounts"][1]["BIC"]
            assert "EUR" == fund["subscriptionBankAccounts"][1]["Currency"]

    @pytest.mark.parametrize("auth", invalid_auths)
    def test_find_fund_invalid_auth(self, client: TestClient, backend_mysql: MySqlContainer,
                                    keycloak: KeycloakContainer, auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            fund_id = fund_ids["passivetest01"]
            response = client.get(f"/v1/funds/{fund_id}", auth=auth)
            assert response.status_code == 403

    def test_find_fund_anonymous(self, client: TestClient, backend_mysql: MySqlContainer,
                                 keycloak: KeycloakContainer, anonymous_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            fund_id = fund_ids["passivetest01"]
            response = client.get(f"/v1/funds/{fund_id}", auth=anonymous_auth)
            assert response.status_code == 200

    def test_find_fund_unauthorized(self, client: TestClient, backend_mysql: MySqlContainer,
                                    keycloak: KeycloakContainer):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            fund_id = fund_ids["passivetest01"]
            response = client.get(f"/v1/funds/{fund_id}")
            assert response.status_code == 403

    def test_find_fund_invalid_id(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            for invalid_uuid in invalid_uuids:
                url = f"/v1/funds/{invalid_uuid}"
                response = client.get(url, auth=user_1_auth)
                assert response.status_code == 400

    def test_list_funds(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            response = client.get("/v1/funds", auth=user_1_auth)
            assert response.status_code == 200

            response_funds = response.json()
            response_ids = list(map(lambda i: i["id"], response_funds))
            assert 7 == len(response_funds)
            for fund_id in fund_ids.values():
                assert fund_id in response_ids

    @pytest.mark.parametrize("auth", invalid_auths)
    def test_list_funds_invalid_auth(self, client: TestClient, backend_mysql: MySqlContainer,
                                     keycloak: KeycloakContainer, auth: BearerAuth):
        response = client.get(f"/v1/funds", auth=auth)
        assert response.status_code == 403

    def test_list_funds_anonymous(self, client: TestClient, backend_mysql: MySqlContainer,
                                  keycloak: KeycloakContainer, anonymous_auth: BearerAuth):
        response = client.get(f"/v1/funds", auth=anonymous_auth)
        assert response.status_code == 200

    def test_list_funds_unauthorized(self, client: TestClient, backend_mysql: MySqlContainer,
                                     keycloak: KeycloakContainer):
        response = client.get(f"/v1/funds")
        assert response.status_code == 403

    def test_list_funds_limits(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            self.assert_list(
                client=client,
                auth=user_1_auth,
                first_result=0,
                max_results=3,
                expected_ids=[
                    fund_ids["passivetest01"],
                    fund_ids["activetest01"],
                    fund_ids["balancedtst01"]
                ]
            )

            self.assert_list(
                client=client,
                auth=user_1_auth,
                first_result=2,
                max_results=8,
                expected_ids=[
                    fund_ids["balancedtst01"],
                    fund_ids["fixedtest0"],
                    fund_ids["dimetest01"],
                    fund_ids["spiltan_test"],
                    fund_ids["HEX25ETF"],
                ]
            )

            self.assert_list(
                client=client,
                auth=user_1_auth,
                first_result=2,
                max_results=2,
                expected_ids=[
                    fund_ids["balancedtst01"],
                    fund_ids["fixedtest0"]
                ]
            )

    @staticmethod
    def assert_list(expected_ids: List[str],
                    client: TestClient,
                    auth: BearerAuth,
                    first_result: int,
                    max_results: int
                    ):
        response = client.get(f"/v1/funds?firstResult={first_result}&maxResults={max_results}", auth=auth)
        assert response.status_code == 200
        response_json = response.json()
        response_ids = list(map(lambda i: i["id"], response_json))
        assert response_ids == expected_ids, \
            f"Fund list with first_result {first_result}, max_results {max_results} to yield {expected_ids}"
