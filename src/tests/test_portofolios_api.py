from .fixtures.client import *  # noqa
from .fixtures.users import *  # noqa
from .fixtures.salkku_mysql import *  # noqa
from .fixtures.backend_mysql import *  # noqa
from .fixtures.sync import *  # noqa
from .fixtures.kafka import *  # noqa
from .fixtures.kafka_connect import *  # noqa
from .fixtures.zookeeper import *  # noqa
from decimal import Decimal
from sqlalchemy import create_engine

from .utils.database import sql_backend_company, sql_backend_securtiy, sql_backend_portfolio_log, \
    sql_backend_portfolio_transaction, sql_backend_last_rate, sql_backend_portfolio, wait_for_row_count
from ..database.models import Company, Security, LastRate, Portfolio, PortfolioTransaction, PortfolioLog

logger = logging.getLogger(__name__)


class TestPortfolio:

    def test_find_portfolio(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        """
        test to find portfolio from portfolio id
        valid results
        +----------------+-------------+---------------+-------------------------+
        | fund           | totalAmount | purchaseTotal | marketValueTotal        |
        +----------------+-------------+---------------+-------------------------+
        | ACTIVETEST01   | 1503.145300 |      20000.00 |  21218.8499983900000000 |
        | BALANCEDTEST01 |  230.527500 |      15000.00 |   2829.6559042500000000 |
        | DIMETEST01     |  614.740000 |      40000.00 | 807405.6634000000000000 |
        | PASSIVETEST01  |  490.812000 |      20000.00 |  43214.1805956000000000 |
        | SPILTAN TEST   |  233.527500 |      15000.00 |   9156.5432167500000000 |
        +----------------+-------------+---------------+-------------------------+
        """
        portfolio_table_id = "6bb05ba3-2b4f-4031-960f-0f20d5244440"
        total_amounts = [Decimal("1503.145300"), Decimal("230.527500"), Decimal("614.740000"), Decimal("490.812000"),
                         Decimal("233.527500")]
        purchase_total = [Decimal("20000.00"), Decimal("15000.00"), Decimal("40000.00"), Decimal("20000.00"),
                              Decimal("15000.00")]
        market_value_total = [Decimal("21218.8499983900000000"), Decimal("2829.6559042500000000"),
                          Decimal("807405.6634000000000000"), Decimal("43214.1805956000000000"),
                          Decimal("9156.5432167500000000")]
        expected_sum_total_amounts = sum(total_amounts)
        expected_sum_market_value_total = sum(market_value_total)
        expected_sum_purchase_total = sum(purchase_total)
        tables = [(Company, 4), (Security, 5), (LastRate, 6), (Portfolio, 5), (PortfolioTransaction, 30)]
        engine = create_engine(backend_mysql.get_connection_url())

        with sql_backend_company(backend_mysql), sql_backend_securtiy(backend_mysql), sql_backend_last_rate(
                backend_mysql), sql_backend_portfolio(backend_mysql), sql_backend_portfolio_transaction(backend_mysql):
            for table in tables:
                wait_for_row_count(engine=engine, entity=table[0], count=table[1])
            response = client.get(f"/v1/portfolios/{portfolio_table_id}", auth=user_1_auth)
            assert response.status_code == 200
            values = response.json(parse_float=Decimal)

            assert 4 == len(values)
            assert portfolio_table_id == values["id"]
            assert expected_sum_total_amounts == values["totalAmount"]
            assert expected_sum_market_value_total == values["marketValueTotal"]
            assert expected_sum_purchase_total == values["purchaseTotal"]
            assert type(values) == Portfolio

    @pytest.mark.skip
    def test_get_portfolio_summary(self, client: TestClient, user_1_auth: BearerAuth, backend_mysql: MySqlContainer):
        """
        test to find portfolio history from portfolio id in a given period
        """
        portfolio_id = "123"
        start_date = ""
        end_date = ""
        response = client.get(
            f"/v1/portfolios/{portfolio_id}/summary?startDate={start_date}&endDate={end_date}",
            auth=user_1_auth)
        assert response.status_code == 200
        values = response.json()
        assert 2 == len(values)

    @pytest.mark.skip
    def test_portfolio_history_values(self):
        pass  # todo development after new database changes

    @pytest.mark.skip
    def test_list_portfolios(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        """
        test to list portfolios of a user
        """
        tables = [(Company, 4), (Security,5), (LastRate,6), (Portfolio,5), (PortfolioTransaction,30)]
        engine = create_engine(backend_mysql.get_connection_url())
        with sql_backend_company(backend_mysql), sql_backend_securtiy(backend_mysql), sql_backend_last_rate(
                backend_mysql), sql_backend_portfolio(backend_mysql), sql_backend_portfolio_transaction(backend_mysql):
            for table in tables:
                wait_for_row_count(engine=engine, entity=table[0], count=table[1])

            response = client.get("/v1/portfolios/", auth=user_1_auth)
            import pdb
            pdb.set_trace()
            assert response.status_code == 200
            values = response.json()
            assert 1 == len(values)
            assert "self.expected_sum_total_amount" == values[0]["totalAmount"]
            assert "self.expected_sum_market_value_total" == values[0]["marketValueTotal"]
            assert "self.expected_sum_purchase_total" == values[0]["purchaseTotal"]
