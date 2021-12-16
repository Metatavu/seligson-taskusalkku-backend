import logging

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

from .constants import security_ids

from .utils.database import sql_backend_company, sql_backend_security, sql_backend_portfolio_log, \
    sql_backend_portfolio_transaction, sql_backend_last_rate, sql_backend_portfolio, sql_backend_funds, \
    sql_backend_security_rates, wait_for_row_count

from ..database.models import Company, Security, LastRate, Portfolio, PortfolioTransaction, PortfolioLog

import logging

logger = logging.getLogger(__name__)

"""
Portfolio values from the database

6bb05ba3-2b4f-4031-960f-0f20d5244440
+-------------+---------------+-------------------------+
| totalamount | purchaseTotal | marketValueTotal        |
+-------------+---------------+-------------------------+
|  490.812000 |      20000.00 |  43214.1805956000000000 |
| 1503.145300 |      20000.00 |  21218.8499983900000000 |
|  230.527500 |      15000.00 |   2829.6559042500000000 |
|  614.740000 |      40000.00 | 807405.6634000000000000 |
+-------------+---------------+-------------------------+

84da0adf-db11-4be9-8c51-fcebc05a1d4f
+-------------+---------------+-------------------------+
| totalamount | purchaseTotal | marketValueTotal        |
+-------------+---------------+-------------------------+
|    1.709800 |         79.00 |    150.5415637400000000 |
|  153.685000 |      10000.00 | 201851.4158500000000000 |
+-------------+---------------+-------------------------+
ba4869f3-dff4-409f-9208-69503f88f228
No results

10b9cf58-669a-492a-9fb4-91e18129916d
+-------------+---------------+-----------------------+
| totalamount | purchaseTotal | marketValueTotal      |
+-------------+---------------+-----------------------+
|   76.842500 |       5000.00 | 6765.6978077500000000 |
|   76.842500 |       5000.00 | 1084.7317827500000000 |
+-------------+---------------+-----------------------+

c510d0a5-78bf-454d-af64-75587e9cc315
+-------------+---------------+-----------------------+
| totalamount | purchaseTotal | marketValueTotal      |
+-------------+---------------+-----------------------+
|  153.685000 |      10000.00 | 2169.4635655000000000 |
+-------------+---------------+-----------------------+
"""
portfolio_values = {
    "6bb05ba3-2b4f-4031-960f-0f20d5244440": {
        "total_amounts": [Decimal("1503.145300"), Decimal("230.527500"), Decimal("614.740000"), Decimal("490.812000")],
        "purchase_total": [Decimal("20000.00"), Decimal("15000.00"), Decimal("40000.00"), Decimal("20000.00")],
        "market_value_total": [Decimal("21218.8499983900000000"), Decimal("2829.6559042500000000"),
                               Decimal("807405.6634000000000000"), Decimal("43214.1805956000000000")]
    },
    "84da0adf-db11-4be9-8c51-fcebc05a1d4f": {
        "total_amounts": [Decimal("1.709800"), Decimal("153.685000")],
        "purchase_total": [Decimal("79.00"), Decimal("10000.00")],
        "market_value_total": [Decimal("150.5415637400000000"), Decimal("201851.4158500000000000")]
    },
    "ba4869f3-dff4-409f-9208-69503f88f228": {
        "total_amounts": [],
        "purchase_total": [],
        "market_value_total": []
    },
    "10b9cf58-669a-492a-9fb4-91e18129916d": {
        "total_amounts": [Decimal("76.842500"), Decimal("76.842500")],
        "purchase_total": [Decimal("5000.00"), Decimal("5000.00")],
        "market_value_total": [Decimal("6765.6978077500000000"), Decimal("1084.7317827500000000")]
    },
    "c510d0a5-78bf-454d-af64-75587e9cc315": {
        "total_amounts": [Decimal("153.685000")],
        "purchase_total": [Decimal("10000.00")],
        "market_value_total": [Decimal("2169.4635655000000000")]
    }
}


class TestPortfolio:

    def test_find_portfolio(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        """
        test to find portfolio from portfolio id
        """

        main_portfolio_id = "6bb05ba3-2b4f-4031-960f-0f20d5244440"
        main_expected_sum_total_amounts = sum(portfolio_values[main_portfolio_id]["total_amounts"])
        main_expected_sum_market_value_total = sum(portfolio_values[main_portfolio_id]["market_value_total"])
        main_expected_sum_purchase_total = sum(portfolio_values[main_portfolio_id]["purchase_total"])

        sub_portfolio_id = "84da0adf-db11-4be9-8c51-fcebc05a1d4f"
        sub_expected_sum_total_amounts = sum(portfolio_values[sub_portfolio_id]["total_amounts"])
        sub_expected_sum_market_value_total = sum(portfolio_values[sub_portfolio_id]["market_value_total"])
        sub_expected_sum_purchase_total = sum(portfolio_values[sub_portfolio_id]["purchase_total"])

        tables = [(Company, 4), (Security, 9), (LastRate, 9), (Portfolio, 5), (PortfolioTransaction, 30),
                  (PortfolioLog, 60)]
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

        tables = [(Company, 4), (Security, 9), (LastRate, 9), (Portfolio, 5), (PortfolioTransaction, 30),
                  (PortfolioLog, 60)]
        engine = create_engine(backend_mysql.get_connection_url())
        with sql_backend_company(backend_mysql), sql_backend_funds(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_last_rate(backend_mysql), \
                sql_backend_portfolio(backend_mysql), sql_backend_portfolio_transaction(backend_mysql), \
                sql_backend_portfolio_log(backend_mysql):
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

    def test_portfolio_history_values(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        tables = [(Company, 4), (Security, 9), (LastRate, 9), (Portfolio, 5), (PortfolioTransaction, 30),
                  (PortfolioLog, 60)]
        engine = create_engine(backend_mysql.get_connection_url())
        with sql_backend_company(backend_mysql), sql_backend_funds(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_last_rate(backend_mysql), \
                sql_backend_security_rates(backend_mysql), sql_backend_portfolio(backend_mysql), \
                sql_backend_portfolio_transaction(backend_mysql), sql_backend_portfolio_log(backend_mysql):

            for table in tables:
                wait_for_row_count(engine=engine, entity=table[0], count=table[1])

            portfolio_id = "6bb05ba3-2b4f-4031-960f-0f20d5244440"

            """
            2020-06-01:
             
            3 transfers:
            - subscription of PASSIVETEST01, amount 8.891322479445751
            - redemption of PASSIVETEST01, amount 46.54840931204268 (ignored)
            - transfer from PASSIVETEST01 to ACTIVETEST01, amount  35.19015936647667
            
            security rates:
            - PASSIVETEST01 = 3.0411934114057058
            - ACTIVETEST01 = 2.8414261328219794
            
            Sum for day should be: 
            
            (8.891322479445751 * 3.0411934114057058) + (35.19015936647667 * 2.8414261328219794) 

            2020-06-06
            3. transfers
            - subscription of SPILTAN TEST with amount 25.034593204195833
            - redemption of SPILTAN TEST with amount amount 12.602863875893721 (ignored)
            - transfer from SPILTAN TEST PASSIVETEST01 with amount 14.24559022245685
            
            security rates:
            - SPILTAN TEST = 10.2893454827978
            - PASSIVETEST01 = 2.265510994165496
            - SEK = 5.123123
            
            (25.034593204195833 * 10.2893454827978  / 5.123123) + (14.24559022245685 * 2.265510994165496) 
            
            1998-01-23
            1. transfer
            - subscription of PASSIVETEST01 with amount 30
            - redemption of PASSIVETEST01 with amount 30 (ignored)
            - removal of BALANCEDTEST01 with amount 3.5
            
            security rates:
            - PASSIVETEST01 = 1.5151887883728388
            - BALANCEDTEST01 = 8.510354920492162
            
            and because it's before 1999-01-01, it's in FIM
            
            (30 * 1.5151887883728388 / 5.94573) - (3.5 * 8.510354920492162 / 5.94573)
            """

            expected_value_1998_01_23 = (30 * 1.5151887883728388 / 5.94573) - \
                                        (3.5 * 8.510354920492162 / 5.94573)

            expected_value_2020_06_01 = (8.891322479445751 * 3.0411934114057058) + \
                                        (35.19015936647667 * 2.8414261328219794)

            expected_value_2020_06_06 = (25.034593204195833 * 10.2893454827978 / 5.123123) + \
                                        (14.24559022245685 * 2.265510994165496)

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
            assert 0 == len(responses)

    def test_list_portfolios(self, client: TestClient, backend_mysql: MySqlContainer, user_1_auth: BearerAuth):
        """
        test to list portfolios of a user
        """

        portfolio_table_ids = ["6bb05ba3-2b4f-4031-960f-0f20d5244440", "84da0adf-db11-4be9-8c51-fcebc05a1d4f",
                               "10b9cf58-669a-492a-9fb4-91e18129916d", "ba4869f3-dff4-409f-9208-69503f88f228"]

        tables = [(Company, 4), (Security, 9), (LastRate, 9), (Portfolio, 5), (PortfolioTransaction, 30),
                  (PortfolioLog, 60)]
        engine = create_engine(backend_mysql.get_connection_url())
        with sql_backend_company(backend_mysql), sql_backend_funds(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_last_rate(backend_mysql), \
                sql_backend_portfolio(backend_mysql), sql_backend_portfolio_transaction(backend_mysql), \
                sql_backend_portfolio_log(backend_mysql):
            for table in tables:
                wait_for_row_count(engine=engine, entity=table[0], count=table[1])

            response = client.get("/v1/portfolios/", auth=user_1_auth)
            assert response.status_code == 200
            results = response.json()
            assert 4 == len(results)

            for result in results:
                portfolio_id = result["id"]
                assert portfolio_id in portfolio_table_ids
                expected_sum_total_amounts = sum(portfolio_values[portfolio_id]["total_amounts"])
                expected_sum_market_value_total = sum(portfolio_values[portfolio_id]["market_value_total"])
                expected_sum_purchase_total = sum(portfolio_values[portfolio_id]["purchase_total"])

                assert expected_sum_total_amounts == Decimal(result["totalAmount"])
                assert expected_sum_market_value_total == Decimal(result["marketValueTotal"])
                assert expected_sum_purchase_total == Decimal(result["purchaseTotal"])

    def test_list_portfolio_securities(self, client: TestClient, user_1_auth: BearerAuth, backend_mysql: MySqlContainer):
        """
        +-------------------------------------------------------------+-------------+
        | security          | totalAmount | purchaseTotal | marketValueTotal        |
        +-------------------------------------------------------------+-------------+
        | PASSIVETEST01     |  490.812000 |      20000.00 |  43214.1805956000000000 |
        | ACTIVETEST01      | 1503.145300 |      20000.00 |  21218.8499983900000000 |
        | BALANCEDTEST01    |  230.527500 |      15000.00 |   2829.6559042500000000 |
        | DIMETEST01        |  614.740000 |      40000.00 | 807405.6634000000000000 |
        | SPILTAN TEST      |  233.527500 |      15000.00 |      0.7417133780667051 |
        +-------------------------------------------------------------+-------------+
        """
        tables = [(Company, 4), (Security, 9), (LastRate, 9), (Portfolio, 5), (PortfolioTransaction, 30),
                  (PortfolioLog, 60)]
        engine = create_engine(backend_mysql.get_connection_url())
        with sql_backend_company(backend_mysql), sql_backend_funds(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_last_rate(backend_mysql), \
                sql_backend_portfolio(backend_mysql), sql_backend_portfolio_transaction(backend_mysql), \
                sql_backend_portfolio_log(backend_mysql):
            for table in tables:
                wait_for_row_count(engine=engine, entity=table[0], count=table[1])

            portfolio_id = "6bb05ba3-2b4f-4031-960f-0f20d5244440"

            response = client.get(f"/v1/portfolios/{portfolio_id}/securities", auth=user_1_auth)

            expected_values_map = {
                security_ids["PASSIVETEST01"]: {
                    "amount": Decimal("490.812000"),
                    "purchaseValue": Decimal("20000.00"),
                    "totalValue": Decimal("43214.1805956000000000")
                },
                security_ids["ACTIVETEST01"]: {
                    "amount": Decimal("1503.145300"),
                    "purchaseValue": Decimal("20000.00"),
                    "totalValue": Decimal("21218.8499983900000000")
                },
                security_ids["BALANCEDTEST01"]: {
                    "amount": Decimal("230.527500"),
                    "purchaseValue": Decimal("15000.00"),
                    "totalValue": Decimal("2829.6559042500000000")
                },
                security_ids["DIMETEST01"]: {
                    "amount": Decimal("614.740000"),
                    "purchaseValue": Decimal("40000.00"),
                    "totalValue": Decimal("807405.6634000000000000")
                },
                security_ids["SPILTAN TEST"]: {
                    "amount": Decimal("233.527500"),
                    "purchaseValue": Decimal("15000.00"),
                    "totalValue": Decimal("0.7417133780667051")
                }
            }

            assert response.status_code == 200
            responses = response.json()
            assert 5 == len(responses)
            for response in responses:
                expected_values = expected_values_map[response["id"]]

                assert expected_values is not None
                assert expected_values["amount"] == Decimal(response["amount"]), f"amount does not match on {response['id']} fund"
                assert expected_values["totalValue"] == Decimal(response["totalValue"]), f"totalValue does not match on {response['id']} fund"
                assert expected_values["purchaseValue"] == Decimal(response["purchaseValue"]), f"purchaseValue does not match on {response['id']} fund"

    def test_portfolio_transactions(self, client: TestClient, user_1_auth: BearerAuth, backend_mysql: MySqlContainer):
        """
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
                "id": "4cfdc2bb-ec9d-4fa7-992e-70c3e9f42a3e",
                "securityId": security_ids["BALANCEDTEST01"],
                "targetSecurityId": "87c526df-c4b0-42d2-8202-07c990c725db",
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
                "id": "4d903bbe-4add-4eba-8cee-7de921429f77",
                "securityId": security_ids["FIXEDTEST01"],
                "targetSecurityId": "a2c14970-161b-407a-9961-d1b14739ec2a",
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
            },
            {
                "id": "28a3b470-231d-4533-aa2a-59590b480151",
                "securityId": security_ids["DIMETEST01"],
                "targetSecurityId": "49d73d12-3061-469a-ba67-0b4a906dd4fc",
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
                "id": "96d17db6-4d2d-4524-8287-3a8a4e159998",
                "securityId": security_ids["SPILTAN TEST"],
                "targetSecurityId": "b01f0d42-e133-44f1-a3c2-d0b560b868ae",
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
            }
        ]

        tables = [(Company, 4), (Security, 9), (LastRate, 9), (Portfolio, 5), (PortfolioTransaction, 30),
                  (PortfolioLog, 60)]
        engine = create_engine(backend_mysql.get_connection_url())
        with sql_backend_company(backend_mysql), sql_backend_funds(backend_mysql), \
                sql_backend_security(backend_mysql), sql_backend_last_rate(backend_mysql), \
                sql_backend_portfolio(backend_mysql), sql_backend_portfolio_transaction(backend_mysql), \
                sql_backend_portfolio_log(backend_mysql):

            for table in tables:
                wait_for_row_count(engine=engine, entity=table[0], count=table[1])

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

    @staticmethod
    def get_portfolio(client: TestClient, portfolio_id: str, auth: BearerAuth) -> Portfolio:
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
