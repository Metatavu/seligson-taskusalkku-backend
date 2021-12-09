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

from .utils.database import sql_backend_company, sql_backend_security, sql_backend_portfolio_log, \
    sql_backend_portfolio_transaction, sql_backend_last_rate, sql_backend_portfolio, sql_backend_funds, \
    wait_for_row_count
from ..database.models import Company, Security, LastRate, Portfolio, PortfolioTransaction, PortfolioLog

logger = logging.getLogger(__name__)


class TestPortfolio:

    def test_find_portfolio(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        """
        test to find portfolio from portfolio id

        valid results from direct query from database for main portfolio
        +-------------+---------------+-------------------------+
        | totalamount | purchaseTotal | marketValueTotal        |
        +-------------+---------------+-------------------------+
        |  490.812000 |      20000.00 |  43214.1805956000000000 |
        | 1503.145300 |      20000.00 |  21218.8499983900000000 |
        |  230.527500 |      15000.00 |   2829.6559042500000000 |
        |  614.740000 |      40000.00 | 807405.6634000000000000 |
        +-------------+---------------+-------------------------+

        and for the sub portfolio
        +-------------+---------------+-------------------------+
        | totalamount | purchaseTotal | marketValueTotal        |
        +-------------+---------------+-------------------------+
        |    1.709800 |         79.00 |    150.5415637400000000 |
        |  153.685000 |      10000.00 | 201851.4158500000000000 |
        +-------------+---------------+-------------------------+
        """

        main_portfolio_id = "6bb05ba3-2b4f-4031-960f-0f20d5244440"

        main_total_amounts = [Decimal("1503.145300"), Decimal("230.527500"), Decimal("614.740000"),
                              Decimal("490.812000")]
        main_purchase_total = [Decimal("20000.00"), Decimal("15000.00"), Decimal("40000.00"), Decimal("20000.00")]
        main_market_value_total = [Decimal("21218.8499983900000000"), Decimal("2829.6559042500000000"),
                                   Decimal("807405.6634000000000000"), Decimal("43214.1805956000000000")]
        main_expected_sum_total_amounts = sum(main_total_amounts)
        main_expected_sum_market_value_total = sum(main_market_value_total)
        main_expected_sum_purchase_total = sum(main_purchase_total)

        sub_portfolio_id = "84da0adf-db11-4be9-8c51-fcebc05a1d4f"
        sub_total_amounts = [Decimal("1.709800"), Decimal("153.685000")]
        sub_purchase_total = [Decimal("79.00"), Decimal("10000.00")]
        sub_market_value_total = [Decimal("150.5415637400000000"), Decimal("201851.4158500000000000")]
        sub_expected_sum_total_amounts = sum(sub_total_amounts)
        sub_expected_sum_market_value_total = sum(sub_market_value_total)
        sub_expected_sum_purchase_total = sum(sub_purchase_total)

        tables = [(Company, 4), (Security, 6), (LastRate, 6), (Portfolio, 5), (PortfolioTransaction, 30),
                  (PortfolioLog, 30)]
        engine = create_engine(backend_mysql.get_connection_url())
        with sql_backend_funds(backend_mysql), sql_backend_company(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_last_rate(backend_mysql), \
                sql_backend_portfolio(backend_mysql), sql_backend_portfolio_transaction(backend_mysql), \
                sql_backend_portfolio_log(backend_mysql):
            for table in tables:
                wait_for_row_count(engine=engine, entity=table[0], count=table[1])

            main_portfolio = self.get_portfolio(client=client, portfolio_id=main_portfolio_id, auth=user_1_auth)

            assert 4 == len(main_portfolio)
            assert main_portfolio_id == main_portfolio["id"]
            assert main_expected_sum_total_amounts == Decimal(main_portfolio["totalAmount"])
            assert main_expected_sum_market_value_total == Decimal(main_portfolio["marketValueTotal"])
            assert main_expected_sum_purchase_total == Decimal(main_portfolio["purchaseTotal"])

            sub_portfolio = self.get_portfolio(client=client, portfolio_id=sub_portfolio_id, auth=user_1_auth)

            assert 4 == len(sub_portfolio)
            assert sub_portfolio_id == sub_portfolio["id"]
            assert sub_expected_sum_total_amounts == Decimal(sub_portfolio["totalAmount"])
            assert sub_expected_sum_market_value_total == Decimal(sub_portfolio["marketValueTotal"])
            assert sub_expected_sum_purchase_total == Decimal(sub_portfolio["purchaseTotal"])

    @pytest.mark.skip()
    def test_get_portfolio_summary(self, client: TestClient, user_1_auth: BearerAuth, backend_mysql: MySqlContainer):
        """
        test to find portfolio history from portfolio id in a given period

        valid results from direct query from database for id = 6bb05ba3-2b4f-4031-960f-0f20d5244440 :
        +------------+
        | redemption |
        +------------+
        |   35000.00 |
        +------------+
        +--------------+
        | subscription |
        +--------------+
        |     30099.17 |
        +--------------+

        """

        expected_redemption = Decimal("35000.00")
        expected_subscription = Decimal("30099.17")

        tables = [(Company, 4), (Security, 6), (LastRate, 6), (Portfolio, 5), (PortfolioTransaction, 30),
                  (PortfolioLog, 30)]
        engine = create_engine(backend_mysql.get_connection_url())
        with sql_backend_company(backend_mysql), sql_backend_security(backend_mysql), sql_backend_last_rate(
                backend_mysql), sql_backend_portfolio(backend_mysql), sql_backend_portfolio_transaction(
                backend_mysql), sql_backend_portfolio_log(backend_mysql):
            for table in tables:
                wait_for_row_count(engine=engine, entity=table[0], count=table[1])
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

    @pytest.mark.skip
    def test_portfolio_history_values(self):
        pass  # todo development after new database changes

    @pytest.mark.skip()
    def test_list_portfolios(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        """
        test to list portfolios of a user

        valid results from direct query from database for all portfolios of user_1:

        portfolio_id = 123
        +----------------+-------------+---------------+-------------------------+
        | fund           | totalAmount | purchaseTotal | marketValueTotal        |
        +----------------+-------------+---------------+-------------------------+
        | ACTIVETEST01   | 1503.145300 |      20000.00 |  21218.8499983900000000 |
        | BALANCEDTEST01 |  230.527500 |      15000.00 |   2829.6559042500000000 |
        | DIMETEST01     |  614.740000 |      40000.00 | 807405.6634000000000000 |
        | PASSIVETEST01  |  490.812000 |      20000.00 |  43214.1805956000000000 |
        | SPILTAN TEST   |  233.527500 |      15000.00 |   9156.5432167500000000 |
        +----------------+-------------+---------------+-------------------------+

        portfolio_id = 124
        +---------------+-------------+---------------+-------------------------+
        | fund          | totalAmount | purchaseTotal | marketValueTotal        |
        +---------------+-------------+---------------+-------------------------+
        | DIMETEST01    |  153.685000 |      10000.00 | 201851.4158500000000000 |
        | PASSIVETEST01 |    1.709800 |         79.00 |    150.5415637400000000 |
        +---------------+-------------+---------------+-------------------------+

        portfolio_id = 125
        +---------------+-------------+---------------+-----------------------+
        | fund          | totalAmount | purchaseTotal | marketValueTotal      |
        +---------------+-------------+---------------+-----------------------+
        | ACTIVETEST01  |   76.842500 |       5000.00 | 1084.7317827500000000 |
        | PASSIVETEST01 |   76.842500 |       5000.00 | 6765.6978077500000000 |
        +---------------+-------------+---------------+-----------------------+
        """

        portfolio_table_ids = ["6bb05ba3-2b4f-4031-960f-0f20d5244440", "84da0adf-db11-4be9-8c51-fcebc05a1d4f",
                               "10b9cf58-669a-492a-9fb4-91e18129916d"]
        total_amounts = [[Decimal("1503.145300"), Decimal("230.527500"), Decimal("614.740000"), Decimal("490.812000"),
                          Decimal("233.527500")],
                         [Decimal("153.685000"), Decimal("1.709800")],
                         [Decimal("76.842500"), Decimal("76.842500")],
                         ]
        purchases_total = [[Decimal("20000.00"), Decimal("15000.00"), Decimal("40000.00"), Decimal("20000.00"),
                            Decimal("15000.00")],
                           [Decimal("10000.00"), Decimal("79.00")],
                           [Decimal("5000.00"), Decimal("5000.00")],
                           ]
        market_values_total = [[Decimal("21218.8499983900000000"), Decimal("2829.6559042500000000"),
                                Decimal("807405.6634000000000000"), Decimal("43214.1805956000000000"),
                                Decimal("9156.5432167500000000")],
                               [Decimal("201851.4158500000000000"), Decimal("150.5415637400000000")],
                               [Decimal("1084.7317827500000000"), Decimal("6765.6978077500000000")],
                               ]
        expected_sum_total_amounts = [sum(total_amount) for total_amount in total_amounts]
        expected_sum_market_values_total = [sum(market_values_total) for market_values_total in market_values_total]
        expected_sum_purchases_total = [sum(purchase_total) for purchase_total in purchases_total]

        tables = [(Company, 4), (Security, 6), (LastRate, 6), (Portfolio, 5), (PortfolioTransaction, 30),
                  (PortfolioLog, 30)]
        engine = create_engine(backend_mysql.get_connection_url())
        with sql_backend_company(backend_mysql), sql_backend_security(backend_mysql), sql_backend_last_rate(
                backend_mysql), sql_backend_portfolio(backend_mysql), sql_backend_portfolio_transaction(
                backend_mysql), sql_backend_portfolio_log(backend_mysql):
            for table in tables:
                wait_for_row_count(engine=engine, entity=table[0], count=table[1])

            response = client.get("/v1/portfolios/", auth=user_1_auth)
            assert response.status_code == 200
            values = response.json()
            assert 3 == len(values)
            for idx, portfolio_table_id in enumerate(portfolio_table_ids):
                assert portfolio_table_ids[idx] == values[idx]["id"]
                assert expected_sum_total_amounts[idx] == Decimal(values[idx]["totalAmount"])
                assert expected_sum_market_values_total[idx] == Decimal(values[idx]["marketValueTotal"])
                assert expected_sum_purchases_total[idx] == Decimal(values[idx]["purchaseTotal"])

    @staticmethod
    def get_portfolio(client: TestClient, portfolio_id: str, auth: BearerAuth) -> Portfolio:
        """Finds single portfolio from the API

        Args:
            client (TestClient): client
            portfolio_id (str): portfolio id
            auth (BearerAuth): auth
        Returns:
             Portfolio]: single portfolio
        """
        response = client.get(f"/v1/portfolios/{portfolio_id}", auth=auth)
        assert response.status_code == 200
        return response.json(parse_float=Decimal)
