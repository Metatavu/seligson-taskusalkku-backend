import datetime
import logging

from sqlalchemy import create_engine
import factory.fuzzy
from .fixtures.client import *  # noqa
from .fixtures.users import *  # noqa
from .fixtures.backend_mysql import *  # noqa
from sqlalchemy.orm import scoped_session, sessionmaker

from ..utils.uuid_utils import uuid_to_short_form

logger = logging.getLogger(__name__)


class TestPortfolio:

    def test_find_portfolio(self, client: TestClient, user_1_auth: BearerAuth, mysql: MySqlContainer):
        """
        test to find portfolio from portfolio id
        """

        with sql_backend_portfolio(backend_mysql):
            response = client.get(f"/v1/portfolios/{self.porid}", auth=user_1_auth)
            assert response.status_code == 200
            values = response.json()
            assert 4 == len(values)
            assert uuid_to_short_form(self.porid) == values["id"]
            assert self.expected_sum_total_amount == values["totalAmount"]
            assert self.expected_sum_market_value_total == values["marketValueTotal"]
            assert self.expected_sum_purchase_total == values["purchaseTotal"]

    def test_get_portfolio_h_summary(self, client: TestClient, user_1_auth: BearerAuth, mysql: MySqlContainer):
        """
        test to find portfolio history from portfolio id in a given period
        """
        response = client.get(
            f"/v1/portfolios/{self.porid}/summary?startDate={self.start_date}&endDate={self.end_date}",
            auth=user_1_auth)
        assert response.status_code == 200
        values = response.json()
        assert 2 == len(values)

    def test_portfolio_history_values(self):
        pass  # todo development after new database changes

    def test_list_portfolios(self, client: TestClient, user_1_auth: BearerAuth, mysql: MySqlContainer):
        """
        test to list portfolios of a user
        """
        response = client.get("/v1/portfolios/", auth=user_1_auth)
        assert response.status_code == 200
        values = response.json()
        assert 1 == len(values)
        assert self.expected_sum_total_amount == values[0]["totalAmount"]
        assert self.expected_sum_market_value_total == values[0]["marketValueTotal"]
        assert self.expected_sum_purchase_total == values[0]["purchaseTotal"]
