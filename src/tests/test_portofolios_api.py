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

from .constants import security_ids, invalid_auths, invalid_uuids

from .utils.database import sql_backend_company, sql_backend_security, sql_backend_portfolio_log, \
    sql_backend_portfolio_transaction, sql_backend_last_rate, sql_backend_portfolio, sql_backend_funds, \
    sql_backend_security_rates, sql_backend_company_access

import logging

logger = logging.getLogger(__name__)

portfolio_values = {
    "6bb05ba3-2b4f-4031-960f-0f20d5244440": {
        "total_amounts": {
            security_ids["DIMETEST01"]: Decimal("614.740000"),
            security_ids["BALANCEDTEST01"]: Decimal("230.527500"),
            security_ids["PASSIVETEST01"]: Decimal("490.812000"),
            security_ids["SPILTAN TEST"]: Decimal("233.527500"),
            security_ids["ACTIVETEST01"]: Decimal("1503.145300")
        },
        "purchase_total": {
            security_ids["DIMETEST01"]: Decimal("40000.00"),
            security_ids["BALANCEDTEST01"]: Decimal("15000.00"),
            security_ids["PASSIVETEST01"]: Decimal("20000.00"),
            security_ids["SPILTAN TEST"]: Decimal("15000.00"),
            security_ids["ACTIVETEST01"]: Decimal("20000.00")
        },
        "market_value_total": {
            security_ids["DIMETEST01"]: Decimal("807405.663400000000"),
            security_ids["BALANCEDTEST01"]: Decimal("2829.655904250000"),
            security_ids["PASSIVETEST01"]: Decimal("43214.180595600000"),
            security_ids["SPILTAN TEST"]: Decimal("26.51419078530165486687225818"),
            security_ids["ACTIVETEST01"]: Decimal("21218.849998390000")
        }
    },
    "84da0adf-db11-4be9-8c51-fcebc05a1d4f": {
        "total_amounts": {
            security_ids["DIMETEST01"]: Decimal("153.685000"),
            security_ids["PASSIVETEST01"]: Decimal("1.709800")
        },
        "purchase_total": {
            security_ids["DIMETEST01"]: Decimal("10000.00"),
            security_ids["PASSIVETEST01"]: Decimal("79.00")
        },
        "market_value_total": {
            security_ids["DIMETEST01"]: Decimal("201851.415850000000"),
            security_ids["PASSIVETEST01"]: Decimal("150.541563740000")
        }
    },
    "ba4869f3-dff4-409f-9208-69503f88f228": {
        "total_amounts": {
        },
        "purchase_total": {
        },
        "market_value_total": {
        }
    },
    "10b9cf58-669a-492a-9fb4-91e18129916d": {
        "total_amounts": {
            security_ids["PASSIVETEST01"]: Decimal("76.842500"),
            security_ids["ACTIVETEST01"]: Decimal("76.842500")
        },
        "purchase_total": {
            security_ids["PASSIVETEST01"]: Decimal("5000.00"),
            security_ids["ACTIVETEST01"]: Decimal("5000.00")
        },
        "market_value_total": {
            security_ids["PASSIVETEST01"]: Decimal("6765.697807750000"),
            security_ids["ACTIVETEST01"]: Decimal("1084.731782750000")
        }
    }
}


class TestPortfolio:

    def test_find_portfolio(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        """
        test to find portfolio from portfolio id
        """

        main_portfolio_id = "6bb05ba3-2b4f-4031-960f-0f20d5244440"
        main_expected_sum_total_amounts = sum(portfolio_values[main_portfolio_id]["total_amounts"].values())
        main_expected_sum_market_value_total = sum(portfolio_values[main_portfolio_id]["market_value_total"].values())
        main_expected_sum_purchase_total = sum(portfolio_values[main_portfolio_id]["purchase_total"].values())
        main_portfolio_expected_reference_a = "1012300014"
        main_portfolio_expected_reference_b = "2012300013"
        sub_portfolio_id = "84da0adf-db11-4be9-8c51-fcebc05a1d4f"
        sub_expected_sum_total_amounts = sum(portfolio_values[sub_portfolio_id]["total_amounts"].values())
        sub_expected_sum_market_value_total = sum(portfolio_values[sub_portfolio_id]["market_value_total"].values())
        sub_expected_sum_purchase_total = sum(portfolio_values[sub_portfolio_id]["purchase_total"].values())
        sub_portfolio_expected_reference_a = "1012302012"
        sub_portfolio_expected_reference_b = "2012302011"

        with sql_backend_funds(backend_mysql), sql_backend_company(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_last_rate(backend_mysql), \
                sql_backend_portfolio(backend_mysql), sql_backend_portfolio_transaction(backend_mysql), \
                sql_backend_portfolio_log(backend_mysql):

            main_portfolio = self.get_portfolio(client=client, portfolio_id=main_portfolio_id, auth=user_1_auth)

            assert main_portfolio_id == main_portfolio["id"]
            assert "Main portfolio for 123" == main_portfolio["name"]
            assert main_expected_sum_total_amounts == Decimal(main_portfolio["totalAmount"])
            assert main_expected_sum_market_value_total == Decimal(main_portfolio["marketValueTotal"])
            assert main_expected_sum_purchase_total == Decimal(main_portfolio["purchaseTotal"])
            assert main_portfolio_expected_reference_a == main_portfolio["aReference"]
            assert main_portfolio_expected_reference_b == main_portfolio["bReference"]

            sub_portfolio = self.get_portfolio(client=client, portfolio_id=sub_portfolio_id, auth=user_1_auth)

            assert sub_portfolio_id == sub_portfolio["id"]
            assert "Sub-Portfolio for 123" == sub_portfolio["name"]
            assert sub_expected_sum_total_amounts == Decimal(sub_portfolio["totalAmount"])
            assert sub_expected_sum_market_value_total == Decimal(sub_portfolio["marketValueTotal"])
            assert sub_expected_sum_purchase_total == Decimal(sub_portfolio["purchaseTotal"])
            assert sub_portfolio_expected_reference_a == sub_portfolio["aReference"]
            assert sub_portfolio_expected_reference_b == sub_portfolio["bReference"]

    def test_find_portfolio_invalid_id(self, client: TestClient, backend_mysql: MySqlContainer,
                                       user_1_auth: BearerAuth):
        for invalid_uuid in invalid_uuids:
            self.assert_find_portfolio_fail(
                client=client,
                expected_status=400,
                portfolio_id=invalid_uuid,
                auth=user_1_auth
            )

    @pytest.mark.parametrize("auth", invalid_auths)
    def test_find_portfolio_invalid_auth(self, client: TestClient, backend_mysql: MySqlContainer,
                                         keycloak: KeycloakContainer, auth: BearerAuth):
        self.assert_find_portfolio_fail(
            client=client,
            expected_status=403,
            portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
            auth=auth
        )

    def test_find_portfolio_anonymous(self, client: TestClient, backend_mysql: MySqlContainer,
                                      keycloak: KeycloakContainer, anonymous_auth: BearerAuth):
        self.assert_find_portfolio_fail(
            client=client,
            expected_status=403,
            portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
            auth=anonymous_auth
        )

    def test_find_portfolio_unauthorized(self, client: TestClient, backend_mysql: MySqlContainer,
                                         keycloak: KeycloakContainer):
        self.assert_find_portfolio_fail(
            client=client,
            expected_status=403,
            portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
            auth=None
        )

    def test_find_portfolio_wrong_user(self, client: TestClient, backend_mysql: MySqlContainer,
                                       keycloak: KeycloakContainer, user_2_auth: BearerAuth, user_3_auth: BearerAuth):

        with sql_backend_funds(backend_mysql), sql_backend_company(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_portfolio(backend_mysql):

            self.assert_find_portfolio_fail(
                client=client,
                expected_status=403,
                portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
                auth=user_2_auth
            )

            self.assert_find_portfolio_fail(
                client=client,
                expected_status=403,
                portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
                auth=user_3_auth
            )

    def test_find_portfolio_access(self, client: TestClient, backend_mysql: MySqlContainer, keycloak: KeycloakContainer,
                                   user_1_auth: BearerAuth, user_2_auth: BearerAuth, user_3_auth: BearerAuth):

        with sql_backend_funds(backend_mysql), sql_backend_company(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_portfolio(backend_mysql), \
                sql_backend_company_access(backend_mysql):

            assert self.get_portfolio(
                client=client,
                portfolio_id="ff718890-ee47-4414-8582-d9c541a9b1b3",
                auth=user_2_auth
            ) is not None

            assert self.get_portfolio(
                client=client,
                portfolio_id="ccade0c1-2fea-41b4-b1e7-22b0722b07e5",
                auth=user_2_auth
            ) is not None

            self.assert_find_portfolio_fail(
                client=client,
                portfolio_id="ccade0c1-2fea-41b4-b1e7-22b0722b07e5",
                auth=user_1_auth,
                expected_status=403
            )

    def test_get_portfolio_summary(self, client: TestClient, user_1_auth: BearerAuth, backend_mysql: MySqlContainer):
        """
        test to find portfolio history from portfolio id in a given period

        valid results from direct query from database for id = 6bb05ba3-2b4f-4031-960f-0f20d5244440 :
        +------------+
        | redemption |
        +------------+
        |   30099.17 |
        +------------+
        +--------------+
        | subscription |
        +--------------+
        |     35000.00 |
        +--------------+

        """

        expected_redemption = Decimal("30099.17")
        expected_subscription = Decimal("35000.00")

        with sql_backend_company(backend_mysql), sql_backend_funds(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_last_rate(backend_mysql), \
                sql_backend_portfolio(backend_mysql), sql_backend_portfolio_transaction(backend_mysql), \
                sql_backend_portfolio_log(backend_mysql):

            portfolio_table_id = "6bb05ba3-2b4f-4031-960f-0f20d5244440"
            start_date = "1998-01-23"
            end_date = "1998-03-23"

            response = client.get(
                f"/v1/portfolios/{portfolio_table_id}/summary?startDate={start_date}&endDate={end_date}",
                auth=user_1_auth)

            assert response.status_code == 200
            values = response.json()
            assert 2 == len(values)
            assert expected_redemption == Decimal(values["redemptions"])
            assert expected_subscription == Decimal(values["subscriptions"])

    def test_find_portfolio_summary_invalid_id(self, client: TestClient, backend_mysql: MySqlContainer,
                                               user_1_auth: BearerAuth):
        for invalid_uuid in invalid_uuids:
            self.assert_find_portfolio_summary_fail(
                client=client,
                expected_status=400,
                portfolio_id=invalid_uuid,
                auth=user_1_auth
            )

    @pytest.mark.parametrize("auth", invalid_auths)
    def test_find_portfolio_summary_invalid_auth(self, client: TestClient, backend_mysql: MySqlContainer,
                                                 keycloak: KeycloakContainer, auth: BearerAuth):
        self.assert_find_portfolio_summary_fail(
            client=client,
            expected_status=403,
            portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
            auth=auth
        )

    def test_find_portfolio_summary_anonymous(self, client: TestClient, backend_mysql: MySqlContainer,
                                              keycloak: KeycloakContainer, anonymous_auth: BearerAuth):
        self.assert_find_portfolio_summary_fail(
            client=client,
            expected_status=403,
            portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
            auth=anonymous_auth
        )

    def test_find_portfolio_summary_unauthorized(self, client: TestClient, backend_mysql: MySqlContainer,
                                                 keycloak: KeycloakContainer):
        self.assert_find_portfolio_summary_fail(
            client=client,
            expected_status=403,
            portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
            auth=None
        )

    def test_find_portfolio_summary_wrong_user(self, client: TestClient, backend_mysql: MySqlContainer,
                                               keycloak: KeycloakContainer, user_2_auth: BearerAuth,
                                               user_3_auth: BearerAuth):

        with sql_backend_funds(backend_mysql), sql_backend_company(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_portfolio(backend_mysql):

            self.assert_find_portfolio_summary_fail(
                client=client,
                expected_status=403,
                portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
                auth=user_2_auth
            )

            self.assert_find_portfolio_summary_fail(
                client=client,
                expected_status=403,
                portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
                auth=user_3_auth
            )

    def test_portfolio_history_values(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        with sql_backend_company(backend_mysql), sql_backend_funds(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_last_rate(backend_mysql), \
                sql_backend_security_rates(backend_mysql), sql_backend_portfolio(backend_mysql), \
                sql_backend_portfolio_transaction(backend_mysql), sql_backend_portfolio_log(backend_mysql):

            portfolio_id = "6bb05ba3-2b4f-4031-960f-0f20d5244440"

            expected_value_1998_01_23 = 2.6354
            expected_value_2020_06_01 = 1120.0312
            expected_value_2020_06_06 = 3263.4449

            responses = client.get(f"/v1/portfolios/{portfolio_id}/historyValues?"
                                   f"startDate=1998-01-23&endDate=1998-01-23", auth=user_1_auth).json()
            assert 1 == len(responses)
            assert "1998-01-23" == responses[0]["date"]
            assert round(Decimal(expected_value_1998_01_23), 4) == round(Decimal(responses[0]["value"]), 4)

            responses = client.get(f"/v1/portfolios/{portfolio_id}/historyValues?"
                                   f"startDate=2020-06-01&endDate=2020-06-06", auth=user_1_auth).json()

            assert 6 == len(responses)
            assert "2020-06-01" == responses[0]["date"]
            assert round(Decimal(expected_value_2020_06_01), 4) == round(Decimal(responses[0]["value"]), 4)

            assert "2020-06-06" == responses[5]["date"]
            assert round(Decimal(expected_value_2020_06_06), 4) == round(Decimal(responses[5]["value"]), 4)

            responses = client.get(f"/v1/portfolios/{portfolio_id}/historyValues?"
                                   f"startDate=1999-01-01&endDate=1999-01-01", auth=user_1_auth).json()
            assert 1 == len(responses)

    def test_list_portfolio_history_values_invalid_id(self, client: TestClient, backend_mysql: MySqlContainer,
                                                      user_1_auth: BearerAuth):
        for invalid_uuid in invalid_uuids:
            self.assert_list_portfolio_history_values_fail(
                client=client,
                expected_status=400,
                portfolio_id=invalid_uuid,
                auth=user_1_auth
            )

    @pytest.mark.parametrize("auth", invalid_auths)
    def test_list_portfolio_history_values_invalid_auth(self, client: TestClient, backend_mysql: MySqlContainer,
                                                        keycloak: KeycloakContainer, auth: BearerAuth):
        self.assert_list_portfolio_history_values_fail(
            client=client,
            expected_status=403,
            portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
            auth=auth
        )

    def test_list_portfolio_history_values_anonymous(self, client: TestClient, backend_mysql: MySqlContainer,
                                                     keycloak: KeycloakContainer, anonymous_auth: BearerAuth):
        self.assert_list_portfolio_history_values_fail(
            client=client,
            expected_status=403,
            portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
            auth=anonymous_auth
        )

    def test_list_portfolio_history_values_unauthorized(self, client: TestClient, backend_mysql: MySqlContainer,
                                                        keycloak: KeycloakContainer):
        self.assert_list_portfolio_history_values_fail(
            client=client,
            expected_status=403,
            portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
            auth=None
        )

    def test_list_portfolio_history_values_wrong_user(self, client: TestClient, backend_mysql: MySqlContainer,
                                                      keycloak: KeycloakContainer, user_2_auth: BearerAuth,
                                                      user_3_auth: BearerAuth):

        with sql_backend_funds(backend_mysql), sql_backend_company(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_portfolio(backend_mysql):
            self.assert_list_portfolio_history_values_fail(
                client=client,
                expected_status=403,
                portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
                auth=user_2_auth
            )

            self.assert_list_portfolio_history_values_fail(
                client=client,
                expected_status=403,
                portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
                auth=user_3_auth
            )

    def test_list_portfolio_access(self, client: TestClient, backend_mysql: MySqlContainer,
                                   keycloak: KeycloakContainer, user_2_auth: BearerAuth):

        with sql_backend_funds(backend_mysql), sql_backend_company(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_portfolio(backend_mysql), \
                sql_backend_company_access(backend_mysql):

            user_2_portfolios_response = client.get("/v1/portfolios/", auth=user_2_auth)
            assert user_2_portfolios_response.status_code == 200
            user_2_portfolios = user_2_portfolios_response.json()

            assert 2 == len(user_2_portfolios)

            user_2_portfolio_ids = list(map(lambda i: i["id"], user_2_portfolios))

            assert "ff718890-ee47-4414-8582-d9c541a9b1b3" in user_2_portfolio_ids
            assert "ccade0c1-2fea-41b4-b1e7-22b0722b07e5" in user_2_portfolio_ids

    def test_list_portfolios(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        """
        test to list portfolios of a user
        """

        portfolio_table_ids = ["6bb05ba3-2b4f-4031-960f-0f20d5244440", "84da0adf-db11-4be9-8c51-fcebc05a1d4f",
                               "10b9cf58-669a-492a-9fb4-91e18129916d", "ba4869f3-dff4-409f-9208-69503f88f228"]

        with sql_backend_company(backend_mysql), sql_backend_funds(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_last_rate(backend_mysql), \
                sql_backend_portfolio(backend_mysql), sql_backend_portfolio_transaction(backend_mysql), \
                sql_backend_portfolio_log(backend_mysql):

            response = client.get("/v1/portfolios/", auth=user_1_auth)
            assert response.status_code == 200
            results = response.json()
            assert 4 == len(results)

            for result in results:
                portfolio_id = result["id"]
                assert portfolio_id in portfolio_table_ids
                expected_sum_total_amounts = sum(portfolio_values[portfolio_id]["total_amounts"].values())
                expected_sum_market_value_total = sum(portfolio_values[portfolio_id]["market_value_total"].values())
                expected_sum_purchase_total = sum(portfolio_values[portfolio_id]["purchase_total"].values())

                assert expected_sum_total_amounts == Decimal(result["totalAmount"])
                assert expected_sum_market_value_total == Decimal(result["marketValueTotal"])
                assert expected_sum_purchase_total == Decimal(result["purchaseTotal"])

    @pytest.mark.parametrize("auth", invalid_auths)
    def test_list_portfolios_invalid_auth(self, client: TestClient, backend_mysql: MySqlContainer,
                                          keycloak: KeycloakContainer, auth: BearerAuth):
        self.assert_list_portfolios_fail(
            client=client,
            expected_status=403,
            auth=auth
        )

    def test_list_portfolios_anonymous(self, client: TestClient, backend_mysql: MySqlContainer,
                                       keycloak: KeycloakContainer, anonymous_auth: BearerAuth):
        self.assert_list_portfolios_fail(
            client=client,
            expected_status=403,
            auth=anonymous_auth
        )

    def test_list_portfolios_unauthorized(self, client: TestClient, backend_mysql: MySqlContainer,
                                          keycloak: KeycloakContainer):
        self.assert_list_portfolios_fail(
            client=client,
            expected_status=403,
            auth=None
        )

    def test_list_portfolios_without_permission_to_any(self, client: TestClient, backend_mysql: MySqlContainer,
                                                       keycloak: KeycloakContainer, user_5_auth: BearerAuth):
        with sql_backend_company(backend_mysql), sql_backend_funds(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_last_rate(backend_mysql), \
                sql_backend_portfolio(backend_mysql), sql_backend_portfolio_transaction(backend_mysql), \
                sql_backend_portfolio_log(backend_mysql):

            response = client.get("/v1/portfolios/", auth=user_5_auth)
            assert response.status_code == 200
            results = response.json()
            assert 0 == len(results)

    def test_list_portfolios_without_ssn(self, client: TestClient, backend_mysql: MySqlContainer,
                                         keycloak: KeycloakContainer, user_4_auth: BearerAuth):
        self.assert_list_portfolios_fail(
            client=client,
            expected_status=403,
            auth=user_4_auth
        )

    def test_list_portfolio_securities(self, client: TestClient, user_1_auth: BearerAuth,
                                       backend_mysql: MySqlContainer):
        with sql_backend_company(backend_mysql), sql_backend_funds(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_last_rate(backend_mysql), \
                sql_backend_portfolio(backend_mysql), sql_backend_portfolio_transaction(backend_mysql), \
                sql_backend_portfolio_log(backend_mysql):

            portfolio_id = "6bb05ba3-2b4f-4031-960f-0f20d5244440"

            response = client.get(f"/v1/portfolios/{portfolio_id}/securities", auth=user_1_auth)
            assert response.status_code == 200
            responses = response.json()
            assert 5 == len(responses)
            for response in responses:
                security_id = response["id"]
                total_amounts = portfolio_values[portfolio_id]["total_amounts"][security_id]
                purchase_total = portfolio_values[portfolio_id]["purchase_total"][security_id]
                market_value_total = portfolio_values[portfolio_id]["market_value_total"][security_id]

                assert total_amounts == Decimal(response["amount"]), \
                    f"amount does not match on {response['id']} fund"
                assert market_value_total == Decimal(response["totalValue"]), \
                    f"totalValue does not match on {response['id']} fund"
                assert purchase_total == Decimal(response["purchaseValue"]), \
                    f"purchaseValue does not match on {response['id']} fund"

    def test_list_portfolio_securities_invalid_id(self, client: TestClient, backend_mysql: MySqlContainer,
                                                  user_1_auth: BearerAuth):
        for invalid_uuid in invalid_uuids:
            self.assert_list_portfolio_securities_fail(
                client=client,
                expected_status=400,
                portfolio_id=invalid_uuid,
                auth=user_1_auth
            )

    @pytest.mark.parametrize("auth", invalid_auths)
    def test_list_portfolio_securities_invalid_auth(self, client: TestClient, backend_mysql: MySqlContainer,
                                                    keycloak: KeycloakContainer, auth: BearerAuth):
        self.assert_list_portfolio_securities_fail(
            client=client,
            expected_status=403,
            portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
            auth=auth
        )

    def test_list_portfolio_securities_anonymous(self, client: TestClient, backend_mysql: MySqlContainer,
                                                 keycloak: KeycloakContainer, anonymous_auth: BearerAuth):
        self.assert_list_portfolio_securities_fail(
            client=client,
            expected_status=403,
            portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
            auth=anonymous_auth
        )

    def test_list_portfolio_securities_unauthorized(self, client: TestClient, backend_mysql: MySqlContainer,
                                                    keycloak: KeycloakContainer):
        self.assert_list_portfolio_securities_fail(
            client=client,
            expected_status=403,
            portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
            auth=None
        )

    def test_list_portfolio_securities_wrong_user(self, client: TestClient, backend_mysql: MySqlContainer,
                                                  keycloak: KeycloakContainer, user_2_auth: BearerAuth,
                                                  user_3_auth: BearerAuth):

        with sql_backend_funds(backend_mysql), sql_backend_company(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_portfolio(backend_mysql):
            self.assert_list_portfolio_securities_fail(
                client=client,
                expected_status=403,
                portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
                auth=user_2_auth
            )

            self.assert_list_portfolio_securities_fail(
                client=client,
                expected_status=403,
                portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
                auth=user_3_auth
            )

    def test_portfolio_transactions(self, client: TestClient, user_1_auth: BearerAuth, backend_mysql: MySqlContainer):
        """
        # noqa
        Results from DB between 2020-06-03 and 2020-06-06

        +----------------+---------------+------------------+------------------+-----------+-----------+---------------+--------------+---------+-----------+
        | security       | c_security    | transaction_code | transaction_date | amount    | c_price   | c_total_value | payment_date | c_value | provision |
        +----------------+---------------+------------------+------------------+-----------+-----------+---------------+--------------+---------+-----------+
        | BALANCEDTEST01 | NULL          | 11               | 2020-06-03       | 48.501945 | 41.719267 |         30.00 | 2020-05-31   |   29.94 |      0.06 |
        | BALANCEDTEST01 | NULL          | 12               | 2020-06-03       | 25.144629 |  2.361169 |         30.00 | 2020-05-31   |   29.94 |      0.06 |
        | BALANCEDTEST01 | FIXEDTEST01   | 46               | 2020-06-03       | 33.607215 |  0.186101 |          0.00 | NULL         |    0.00 |      0.00 |
        | FIXEDTEST01    | NULL          | 11               | 2020-06-04       | 38.957855 |  9.454822 |         40.00 | 2020-06-01   |   39.92 |      0.08 |
        | FIXEDTEST01    | NULL          | 12               | 2020-06-04       | 11.768924 |  2.461088 |         40.00 | 2020-06-01   |   39.92 |      0.08 |
        | FIXEDTEST01    | DIMETEST01    | 46               | 2020-06-04       | 35.477421 | 16.634470 |          0.00 | NULL         |    0.00 |      0.00 |
        | DIMETEST01     | NULL          | 12               | 2020-06-05       | 37.389249 | 16.094385 |         10.00 | 2020-06-02   |   10.00 |      0.00 |
        | DIMETEST01     | NULL          | 11               | 2020-06-05       | 49.512876 | 13.877511 |         10.00 | 2020-06-02   |   10.00 |      0.00 |
        | DIMETEST01     | SPILTAN TEST  | 46               | 2020-06-05       | 18.650488 |  5.003667 |          0.00 | NULL         |    0.00 |      0.00 |
        | SPILTAN TEST   | PASSIVETEST01 | 46               | 2020-06-06       | 14.245590 | 39.142442 |          0.00 | NULL         |    0.00 |      0.00 |
        | SPILTAN TEST   | NULL          | 12               | 2020-06-06       | 12.602864 | 23.684736 |         20.00 | 2020-06-03   |   19.96 |      0.04 |
        | SPILTAN TEST   | NULL          | 11               | 2020-06-06       | 25.034593 | 22.167801 |         20.00 | 2020-06-03   |   19.96 |      0.04 |
        +----------------+---------------+------------------+------------------+-----------+-----------+---------------+--------------+---------+-----------+
        """

        expected_response = [
            {
                "id": "1de01320-1b5b-4e72-b4e0-785a98d40739",
                "securityId": security_ids["BALANCEDTEST01"],
                "targetSecurityId": None,
                "transactionType": "SUBSCRIPTION",
                "valueDate": "2020-06-03",
                "value": "29.94",
                "shareAmount": "48.501945",
                "marketValue": "41.719267",
                "totalValue": "30.00",
                "paymentDate": "2020-05-31",
                "provision": "0.06"
            },
            {
                "id": "27062691-7f69-4f18-b96f-10e5097ef90d",
                "securityId": security_ids["FIXEDTEST01"],
                "targetSecurityId": None,
                "transactionType": "SUBSCRIPTION",
                "valueDate": "2020-06-04",
                "value": "39.92",
                "shareAmount": "38.957855",
                "marketValue": "9.454822",
                "totalValue": "40.00",
                "paymentDate": "2020-06-01",
                "provision": "0.08"
            },
            {
                "id": "28a3b470-231d-4533-aa2a-59590b480151",
                "securityId": security_ids["DIMETEST01"],
                "targetSecurityId": security_ids["SPILTAN TEST"],
                "transactionType": "SECURITY",
                "valueDate": "2020-06-05",
                "value": "0.00",
                "shareAmount": "18.650488",
                "marketValue": "5.003667",
                "totalValue": "0.00",
                "paymentDate": None,
                "provision": "0.00"
            },
            {
                "id": "4cfa2d60-aa95-46a6-b0ee-34109b7cf25e",
                "securityId": security_ids["FIXEDTEST01"],
                "targetSecurityId": None,
                "transactionType": "REDEMPTION",
                "valueDate": "2020-06-04",
                "value": "39.92",
                "shareAmount": "11.768924",
                "marketValue": "2.461088",
                "totalValue": "40.00",
                "paymentDate": "2020-06-01",
                "provision": "0.08"
            },
            {
                "id": "4cfdc2bb-ec9d-4fa7-992e-70c3e9f42a3e",
                "securityId": security_ids["BALANCEDTEST01"],
                "targetSecurityId": security_ids["FIXEDTEST01"],
                "transactionType": "SECURITY",
                "valueDate": "2020-06-03",
                "value": "0.00",
                "shareAmount": "33.607215",
                "marketValue": "0.186101",
                "totalValue": "0.00",
                "paymentDate": None,
                "provision": "0.00"
            },
            {
                "id": "4d903bbe-4add-4eba-8cee-7de921429f77",
                "securityId": security_ids["FIXEDTEST01"],
                "targetSecurityId": security_ids["DIMETEST01"],
                "transactionType": "SECURITY",
                "valueDate": "2020-06-04",
                "value": "0.00",
                "shareAmount": "35.477421",
                "marketValue": "16.634470",
                "totalValue": "0.00",
                "paymentDate": None,
                "provision": "0.00"
            },
            {
                "id": "675f50ee-48ff-4709-b53b-97169c5ddc83",
                "securityId": security_ids["SPILTAN TEST"],
                "targetSecurityId": None,
                "transactionType": "SUBSCRIPTION",
                "valueDate": "2020-06-06",
                "value": "19.96",
                "shareAmount": "25.034593",
                "marketValue": "22.167801",
                "totalValue": "20.00",
                "paymentDate": "2020-06-03",
                "provision": "0.04"
            },
            {
                "id": "95453ba7-667f-4460-b36b-0e24f635a708",
                "securityId": security_ids["DIMETEST01"],
                "targetSecurityId": None,
                "transactionType": "REDEMPTION",
                "valueDate": "2020-06-05",
                "value": "10.00",
                "shareAmount": "37.389249",
                "marketValue": "16.094385",
                "totalValue": "10.00",
                "paymentDate": "2020-06-02",
                "provision": "0.00"
            },
            {
                "id": "96d17db6-4d2d-4524-8287-3a8a4e159998",
                "securityId": security_ids["SPILTAN TEST"],
                "targetSecurityId": security_ids["PASSIVETEST01"],
                "transactionType": "SECURITY",
                "valueDate": "2020-06-06",
                "value": "0.00",
                "shareAmount": "14.245590",
                "marketValue": "39.142442",
                "totalValue": "0.00",
                "paymentDate": None,
                "provision": "0.00"
            },
            {
                "id": "98c68a9c-142c-47d0-8b21-4147c952501e",
                "securityId": security_ids["SPILTAN TEST"],
                "targetSecurityId": None,
                "transactionType": "REDEMPTION",
                "valueDate": "2020-06-06",
                "value": "19.96",
                "shareAmount": "12.602864",
                "marketValue": "23.684736",
                "totalValue": "20.00",
                "paymentDate": "2020-06-03",
                "provision": "0.04"
            },
            {
                "id": "bd58f793-00ab-4ad3-804f-fb1cc7a885be",
                "securityId": security_ids["BALANCEDTEST01"],
                "targetSecurityId": None,
                "transactionType": "REDEMPTION",
                "valueDate": "2020-06-03",
                "value": "29.94",
                "shareAmount": "25.144629",
                "marketValue": "2.361169",
                "totalValue": "30.00",
                "paymentDate": "2020-05-31",
                "provision": "0.06"
            },
            {
                "id": "ee6f5135-a88b-4852-b3be-8e4503d434f8",
                "securityId": security_ids["DIMETEST01"],
                "targetSecurityId": None,
                "transactionType": "SUBSCRIPTION",
                "valueDate": "2020-06-05",
                "value": "10.00",
                "shareAmount": "49.512876",
                "marketValue": "13.877511",
                "totalValue": "10.00",
                "paymentDate": "2020-06-02",
                "provision": "0.00"
            }
        ]

        with sql_backend_company(backend_mysql), sql_backend_funds(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_last_rate(backend_mysql), \
                sql_backend_portfolio(backend_mysql), sql_backend_portfolio_transaction(backend_mysql), \
                sql_backend_portfolio_log(backend_mysql):

            portfolio_id = "6bb05ba3-2b4f-4031-960f-0f20d5244440"

            query = "startDate=2020-06-03&endDate=2020-06-06"
            list_response = client.get(f"/v1/portfolios/{portfolio_id}/transactions?{query}", auth=user_1_auth)
            assert list_response.status_code == 200
            responses = list_response.json()
            assert len(expected_response) == len(responses)
            assert expected_response == list_response.json()

            for transaction_type in ["SUBSCRIPTION", "REDEMPTION", "SECURITY"]:
                type_expected = list(filter(lambda i: i["transactionType"] == transaction_type, expected_response))
                query = f"startDate=2020-06-03&endDate=2020-06-06&transactionType={transaction_type}"
                type_response = client.get(f"/v1/portfolios/{portfolio_id}/transactions?{query}", auth=user_1_auth)
                assert type_response.json() == type_expected

            find_expected = expected_response[7]
            find_id = find_expected["id"]
            find_response = client.get(f"/v1/portfolios/{portfolio_id}/transactions/{find_id}", auth=user_1_auth)
            assert find_response.status_code == 200
            assert find_expected == find_response.json()

    def test_list_portfolio_transactions_invalid_id(self, client: TestClient, backend_mysql: MySqlContainer,
                                                    user_1_auth: BearerAuth):
        for invalid_uuid in invalid_uuids:
            self.assert_list_portfolio_transactions_fail(
                client=client,
                expected_status=400,
                portfolio_id=invalid_uuid,
                auth=user_1_auth
            )

    @pytest.mark.parametrize("auth", invalid_auths)
    def test_list_portfolio_transactions_invalid_auth(self, client: TestClient, backend_mysql: MySqlContainer,
                                                      keycloak: KeycloakContainer, auth: BearerAuth):
        self.assert_list_portfolio_transactions_fail(
            client=client,
            expected_status=403,
            portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
            auth=auth
        )

    def test_list_portfolio_transactions_anonymous(self, client: TestClient, backend_mysql: MySqlContainer,
                                                   keycloak: KeycloakContainer, anonymous_auth: BearerAuth):
        self.assert_list_portfolio_transactions_fail(
            client=client,
            expected_status=403,
            portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
            auth=anonymous_auth
        )

    def test_list_portfolio_transactions_unauthorized(self, client: TestClient, backend_mysql: MySqlContainer,
                                                      keycloak: KeycloakContainer):
        self.assert_list_portfolio_transactions_fail(
            client=client,
            expected_status=403,
            portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
            auth=None
        )

    def test_list_portfolio_transactions_wrong_user(self, client: TestClient, backend_mysql: MySqlContainer,
                                                    keycloak: KeycloakContainer, user_2_auth: BearerAuth,
                                                    user_3_auth: BearerAuth):

        with sql_backend_funds(backend_mysql), sql_backend_company(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_portfolio(backend_mysql):
            self.assert_list_portfolio_transactions_fail(
                client=client,
                expected_status=403,
                portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
                auth=user_2_auth
            )

            self.assert_list_portfolio_transactions_fail(
                client=client,
                expected_status=403,
                portfolio_id="6bb05ba3-2b4f-4031-960f-0f20d5244440",
                auth=user_3_auth
            )

    @staticmethod
    def assert_find_portfolio_fail(client: TestClient, expected_status: int, portfolio_id: str,
                                   auth: Optional[BearerAuth]):
        if auth is None:
            response = client.get(f"/v1/portfolios/{portfolio_id}")
        else:
            response = client.get(f"/v1/portfolios/{portfolio_id}", auth=auth)

        assert expected_status == response.status_code

    @staticmethod
    def assert_list_portfolio_securities_fail(client: TestClient, expected_status: int, portfolio_id: str,
                                              auth: Optional[BearerAuth]):
        if auth is None:
            response = client.get(f"/v1/portfolios/{portfolio_id}/securities")
        else:
            response = client.get(f"/v1/portfolios/{portfolio_id}/securities", auth=auth)

        assert expected_status == response.status_code

    @staticmethod
    def assert_find_portfolio_summary_fail(client: TestClient, expected_status: int, portfolio_id: str,
                                           auth: Optional[BearerAuth]):

        start_date = "1998-01-23"
        end_date = "1998-03-23"

        if auth is None:
            response = client.get(f"/v1/portfolios/{portfolio_id}/summary?startDate={start_date}&endDate={end_date}")
        else:
            response = client.get(f"/v1/portfolios/{portfolio_id}/summary?startDate={start_date}&endDate={end_date}",
                                  auth=auth)

        assert expected_status == response.status_code

    @staticmethod
    def assert_list_portfolio_history_values_fail(client: TestClient, expected_status: int, portfolio_id: str,
                                                  auth: Optional[BearerAuth]):

        start_date = "1998-01-23"
        end_date = "1998-03-23"

        if auth is None:
            response = client.get(f"/v1/portfolios/{portfolio_id}/historyValues?startDate={start_date}" +
                                  f"&endDate={end_date}")
        else:
            response = client.get(f"/v1/portfolios/{portfolio_id}/historyValues?startDate={start_date}" +
                                  f"&endDate={end_date}", auth=auth)

        assert expected_status == response.status_code

    @staticmethod
    def assert_list_portfolio_transactions_fail(client: TestClient, expected_status: int, portfolio_id: str,
                                                auth: Optional[BearerAuth]):

        start_date = "1998-01-23"
        end_date = "1998-03-23"

        if auth is None:
            response = client.get(f"/v1/portfolios/{portfolio_id}/transactions?startDate={start_date}" +
                                  f"&endDate={end_date}")
        else:
            response = client.get(f"/v1/portfolios/{portfolio_id}/transactions?startDate={start_date}" +
                                  f"&endDate={end_date}", auth=auth)

        assert expected_status == response.status_code

    @staticmethod
    def assert_list_portfolios_fail(client: TestClient, expected_status: int, auth: Optional[BearerAuth]):
        if auth is None:
            response = client.get(f"/v1/portfolios")
        else:
            response = client.get(f"/v1/portfolios", auth=auth)

        assert expected_status == response.status_code

    @staticmethod
    def get_portfolio(client: TestClient, portfolio_id: str, auth: BearerAuth) -> Dict[str, any]:
        """Finds single portfolio from the API

        Args:
            client (TestClient): client
            portfolio_id (str): portfolio id
            auth (BearerAuth): auth
        Returns:
             [Portfolio]: single portfolio
        """
        response = client.get(f"/v1/portfolios/{portfolio_id}", auth=auth)
        assert response.status_code == 200
        return response.json(parse_float=Decimal)
