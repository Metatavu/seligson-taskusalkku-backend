import uuid
from typing import Optional

from ..database.models import Fund, SecurityRate
from .utils.database import wait_for_row_count, sql_backend_security_rates, sql_funds_rate

from .constants import fund_ids, invalid_uuids, security_ids, invalid_auths
from .fixtures.backend_mysql import *  # noqa
from .fixtures.client import *  # noqa
from .fixtures.kafka import *  # noqa
from .fixtures.kafka_connect import *  # noqa
from .fixtures.salkku_mysql import *  # noqa
from .fixtures.funds_mssql import *  # noqa
from .fixtures.sync import *  # noqa
from .fixtures.users import *  # noqa
from .fixtures.zookeeper import *  # noqa
from .utils.database import sql_backend_security, sql_backend_funds
from sqlalchemy import create_engine

import logging

logger = logging.getLogger(__name__)

security_1_data = {
    "id": security_ids["ACTIVETEST01"],
    "fundId": fund_ids["activetest01"],
    "name": {
        "fi": "Seligson & Co FI - Active test 1 (VA)",
        "sv": "Seligson & Co SV - Active test 1 (VA)",
        "en": "Seligson & Co EN - Active test 1 (VA)"
    },
    "currency": "EUR"
}

security_3_data = {
    "id": security_ids["PASSIVETEST01"],
    "fundId": fund_ids["passivetest01"],
    "name": {
        "fi": "Seligson & Co FI - Passive test 1 (A)",
        "sv": "Seligson & Co SV - Passive test 1 (A)",
        "en": "Seligson & Co EN - Passive test 1 (A)"
    },
    "currency": "EUR"
}

security_6_data = {
    "id": security_ids["SPILTAN TEST"],
    "fundId": fund_ids["spiltan_test"],
    "name": {
        "fi": "Seligson & Co FI - Spiltan test 1",
        "sv": "Seligson & Co SV - Spiltan test 1",
        "en": "Seligson & Co EN - Spiltan test 1"
    },
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

            assert 7 == len(response_securities)

            assert response_securities[0] == security_1_data
            assert response_securities[6] == security_6_data

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
            assert 7 == len(response.json())

    def test_list_securities_unauthorized(self, client: TestClient, backend_mysql: MySqlContainer,
                                          keycloak: KeycloakContainer):
        with sql_backend_funds(backend_mysql):
            self.assert_list_securities_fail(
                client=client,
                expected_status=403,
                auth=None
            )

    def test_list_securities_series_ids(self, client: TestClient, backend_mysql: MySqlContainer,
                                        user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):

            series_id = 1

            response = client.get(f"/v1/securities?seriesId={series_id}", auth=user_1_auth)
            assert response.status_code == 200

            response_securities = response.json()
            assert 4 == len(response_securities)
            assert response_securities[0] == security_1_data
            assert response_securities[3] == security_3_data

    def test_list_security_history_values(self, client: TestClient, backend_mysql: MySqlContainer,
                                          user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql), \
                sql_backend_security_rates(backend_mysql):
            security_id = security_ids["PASSIVETEST01"]
            start_date = "2020-01-01"
            end_date = "2020-01-05"
            response = client.get(f"/v1/securities/{security_id}/historyValues/"
                                  f"?startDate={start_date}&endDate={end_date}",
                                  auth=user_1_auth)

            assert response.status_code == 200

            values = response.json()
            assert 5 == len(values)
            assert "2020-01-01" == values[0]["date"]
            assert "2020-01-05" == values[4]["date"]
            assert "0.564846" == values[0]["value"]
            assert "1.665009" == values[4]["value"]

    @pytest.mark.parametrize("auth", invalid_auths)
    def test_list_security_history_values_invalid_auth(self, client: TestClient, backend_mysql: MySqlContainer,
                                                       keycloak: KeycloakContainer, auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql), \
                sql_backend_security_rates(backend_mysql):
            security_id = security_ids["PASSIVETEST01"]
            start_date = "2020-01-01"
            end_date = "2020-01-05"
            response = client.get(f"/v1/securities/{security_id}/historyValues/?"
                                  f"startDate={start_date}&endDate={end_date}",
                                  auth=auth)
            assert response.status_code == 403

    def test_list_security_history_values_anonymous(self, client: TestClient, backend_mysql: MySqlContainer,
                                                    keycloak: KeycloakContainer, anonymous_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql), \
                sql_backend_security_rates(backend_mysql):
            security_id = security_ids["PASSIVETEST01"]
            start_date = "2020-01-01"
            end_date = "2020-01-05"
            response = client.get(f"/v1/securities/{security_id}/historyValues/?"
                                  f"startDate={start_date}&endDate={end_date}",
                                  auth=anonymous_auth)
            assert response.status_code == 200

    def test_list_security_history_values_unauthorized(self, client: TestClient, backend_mysql: MySqlContainer,
                                                       keycloak: KeycloakContainer):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql), \
                sql_backend_security_rates(backend_mysql):
            security_id = security_ids["PASSIVETEST01"]
            start_date = "2020-01-01"
            end_date = "2020-01-05"
            response = client.get(f"/v1/securities/{security_id}/historyValues/?"
                                  f"startDate={start_date}&endDate={end_date}")
            assert response.status_code == 403

    def test_sync_security_rates(self,
                                 client: TestClient,
                                 backend_mysql: MySqlContainer,
                                 salkku_mysql: MySqlContainer,
                                 funds_mssql: SqlServerContainer,
                                 kafka_connect: KafkaConnectContainer,
                                 sync: SyncContainer,
                                 user_1_auth: BearerAuth
                                 ):
        engine = create_engine(backend_mysql.get_connection_url())
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            wait_for_row_count(engine=engine, entity=Fund, count=7)

            with sql_funds_rate(mssql=funds_mssql):
                wait_for_row_count(engine=engine, entity=SecurityRate, count=546)
                security_id = security_ids["PASSIVETEST01"]

                start_date = "2020-01-01"
                end_date = "2020-01-05"

                response = client.get(
                    f"/v1/securities/{security_id}/historyValues/?startDate={start_date}&endDate={end_date}",
                    auth=user_1_auth)
                assert response.status_code == 200

                values = response.json()
                assert 5 == len(values)
                assert "2020-01-01" == values[0]["date"]
                assert "2020-01-05" == values[4]["date"]
                assert "0.654115" == values[0]["value"]
                assert "4.743263" == values[4]["value"]

            mysql_exec_sql(mysql=backend_mysql, sql_file="backend-security-rates-teardown.sql")

    def test_find_securities_by_fund_id(self, client: TestClient, backend_mysql: MySqlContainer,
                                        user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            fund_id = fund_ids["activetest01"]
            response = client.get(f"/v1/securities?fundId={fund_id}", auth=user_1_auth)
            assert response.status_code == 200
            security = response.json()
            assert security[0] == security_1_data

    def test_find_security_by_non_existing_fund_id(self, client: TestClient, backend_mysql: MySqlContainer,
                                                   user_1_auth: BearerAuth):
        with sql_backend_funds(backend_mysql), sql_backend_security(backend_mysql):
            fund_id = "541f8d59-50ae-4953-bc1a-432fe33517e3"
            response = client.get(f"/v1/securities?fundId={fund_id}", auth=user_1_auth)
            assert response.status_code == 200
            security = response.json()
            assert security == []

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
