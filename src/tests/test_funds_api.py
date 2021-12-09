from typing import List
from sqlalchemy import create_engine

from ..database.models import Fund, SecurityRate

from .utils.database import wait_for_row_count, sql_backend_funds, sql_backend_security_rates, \
    sql_salkku_fund_securities, sql_salkku_raterah, sql_backend_security

from .fixtures.client import *  # noqa
from .fixtures.users import *  # noqa
from .fixtures.salkku_mysql import *  # noqa
from .fixtures.backend_mysql import *  # noqa
from .fixtures.sync import *  # noqa
from .fixtures.kafka import *  # noqa
from .fixtures.kafka_connect import *  # noqa
from .fixtures.zookeeper import *  # noqa

logger = logging.getLogger(__name__)

fund_ids = {
  "passivetest01": "03568d76-93f1-3a2d-9ed5-b95516546548",
  "activetest01": "dc856547-449b-306e-80c9-05ef8a002a3a",
  "balancedtst01": "3073d4fe-78cc-36ec-a7e0-9c24944030b0",
  "fixedtest0": "8cd9b437-e524-3926-a3f9-969923cf51bd",
  "dimetest01": "79f8da68-6bdc-3a24-acde-327aa14e2546",
  "spiltan_test": "098a999d-65ae-3746-900b-b0b33a5d7d9c"
}

invalid_uuids = ["potato", "`?%!", "äö", "Правда"]


class TestFunds:
    """Tests for funds endpoints"""

    def test_find_fund(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql):
            fund_id = fund_ids["passivetest01"]
            response = client.get(f"/v1/funds/{fund_id}", auth=user_1_auth)
            assert response.status_code == 200

            fund = response.json()
            assert fund_id == fund["id"]
            assert "Passive test fund 1 - fi" == fund["name"]["fi"]
            assert "Passive test fund 1 - en" == fund["name"]["sv"]
            assert "Passive test fund 1 - fi, long" == fund["longName"]["fi"]
            assert "Passive test fund 1 - en, long" == fund["longName"]["sv"]
            assert "Passive test fund 1 - fi, short" == fund["shortName"]["fi"]
            assert "Passive test fund 1 - en, short" == fund["shortName"]["sv"]
            assert "#123456" == fund["color"]
            assert 1 == fund["risk"]
            assert {"fi": "PASSIVETESTFI", "sv": "PASSIVETESTSV"} == fund["KIID"]
            assert "Passive test fund 1 - subs" == fund["bankReceiverName"]
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

    def test_find_fund_invalid_id(self, client: TestClient, backend_mysql: MySqlContainer,  user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql):
            for invalid_uuid in invalid_uuids:
                url = f"/v1/funds/{invalid_uuid}"
                response = client.get(url, auth=user_1_auth)
                assert response.status_code == 400

    def test_list_funds(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql):
            response = client.get("/v1/funds", auth=user_1_auth)
            assert response.status_code == 200

            response_funds = response.json()
            response_ids = list(map(lambda i: i["id"], response_funds))
            assert 6 == len(response_funds)
            for fund_id in fund_ids.values():
                assert fund_id in response_ids

    def test_list_funds_limits(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql):
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
                  fund_ids["spiltan_test"]
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

    def test_find_fund_values(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql), \
                sql_backend_security_rates(backend_mysql):
            fund_id = fund_ids["passivetest01"]
            start_date = "2020-01-01"
            end_date = "2020-01-05"
            response = client.get(f"/v1/funds/{fund_id}/historicalValues/?startDate={start_date}&endDate={end_date}",
                                  auth=user_1_auth)

            assert response.status_code == 200

            values = response.json()
            assert 5 == len(values)
            assert "2020-01-01" == values[0]["date"]
            assert "2020-01-05" == values[4]["date"]
            assert 0.564846 == values[0]["value"]
            assert 1.665009 == values[4]["value"]

    @pytest.mark.skip
    def test_sync_funds(self,
                        client: TestClient,
                        backend_mysql: MySqlContainer,
                        salkku_mysql: MySqlContainer,
                        kafka_connect: KafkaConnectContainer,
                        sync: SyncContainer,
                        user_1_auth: BearerAuth
                        ):
        engine = create_engine(backend_mysql.get_connection_url())
        with sql_salkku_fund_securities(mysql=salkku_mysql):
            wait_for_row_count(engine=engine, entity=Fund, count=6)

            response = client.get("/v1/funds", auth=user_1_auth)
            assert response.status_code == 200

            response_funds = response.json()
            response_names = list(map(lambda i: i["name"]["fi"], response_funds))
            assert "Passive test fund 1 - fi" == response_names[0]

        mysql_exec_sql(mysql=backend_mysql, sql_file="backend-funds-teardown.sql")

    @pytest.mark.skip
    def test_sync_fund_rates(self,
                             client: TestClient,
                             backend_mysql: MySqlContainer,
                             salkku_mysql: MySqlContainer,
                             kafka_connect: KafkaConnectContainer,
                             sync: SyncContainer,
                             user_1_auth: BearerAuth
                             ):
        engine = create_engine(backend_mysql.get_connection_url())
        with sql_salkku_fund_securities(mysql=salkku_mysql):
            wait_for_row_count(engine=engine, entity=Fund, count=6)

            with sql_salkku_raterah(mysql=salkku_mysql):
                wait_for_row_count(engine=engine, entity=SecurityRate, count=546)
                fund_id = client.get("/v1/funds?max_results=1", auth=user_1_auth).json()[0]["id"]
                assert fund_id is not None

                start_date = "2020-01-01"
                end_date = "2020-01-05"

                response = client.get(
                    f"/v1/funds/{fund_id}/historicalValues/?startDate={start_date}&endDate={end_date}",
                    auth=user_1_auth)
                assert response.status_code == 200

                values = response.json()
                assert 5 == len(values)
                assert "2020-01-01" == values[0]["date"]
                assert "2020-01-05" == values[4]["date"]
                assert 0.654115 == values[0]["value"]
                assert 4.743263 == values[4]["value"]

            mysql_exec_sql(mysql=backend_mysql, sql_file="backend-security-rates-teardown.sql")
            mysql_exec_sql(mysql=backend_mysql, sql_file="backend-funds-teardown.sql")

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
